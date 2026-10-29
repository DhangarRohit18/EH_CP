"""
WebGuard Technical Security Assessment API Router
Endpoints:
- POST /api/v1/security-assessments: Run technical security evaluation
- GET /api/v1/security-assessments/{id}: Retrieve detailed assessment report
- GET /api/v1/findings: List and filter technical security findings
- GET /api/v1/scopes, POST /api/v1/scopes: Manage authorized assessment scopes
- GET /api/v1/assets, POST /api/v1/assets: Manage discovered asset inventory
- GET /api/v1/developer-security: Run static code security scan and dependency audit
"""

import time
import uuid
import datetime
import json
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models.security import (
    SecurityAssessmentModel,
    SecurityFindingModel,
    CVEMatchModel,
    AssessmentScopeModel,
    DiscoveredAssetModel,
    SecurityAssessRequest,
    SecurityAssessResponse,
    SecurityFindingSchema,
    CVEMatchSchema,
    TechItemSchema,
    ScopeCreateRequest,
    ScopeResponse,
    AssetCreateRequest,
    AssetResponse
)
from ..utils.security import validate_outbound_url
from ..utils.domain_parser import normalize_domain
from ..utils.scope_validator import is_domain_in_authorized_scope, register_scope_domain
from ..utils.dev_security import run_repository_security_scan
from ..adapters.osint_adapter import osint_adapter
from ..adapters.cve_adapter import cve_adapter
from ..analyzers.security_headers import evaluate_security_headers
from ..analyzers.tech_fingerprint import fingerprint_technologies
from ..analyzers.owasp_passive import evaluate_owasp_alignment
from .events import event_broadcaster

router = APIRouter(prefix="/security-assessments", tags=["Technical Security Intelligence"])
findings_router = APIRouter(prefix="/findings", tags=["Security Findings"])
scopes_router = APIRouter(prefix="/scopes", tags=["Authorized Assessment Scopes"])
assets_router = APIRouter(prefix="/assets", tags=["Attack Surface & Asset Inventory"])
devsec_router = APIRouter(prefix="/developer-security", tags=["Developer Security & Code Audit"])

# ============================================================================
# Technical Security Assessment Endpoints
# ============================================================================

@router.post("", response_model=SecurityAssessResponse)
async def create_security_assessment(
    req: SecurityAssessRequest,
    db: Session = Depends(get_db)
):
    start_time = time.perf_counter()
    parsed = urlparse(req.url)
    domain = normalize_domain(req.domain or parsed.hostname or "")

    if not domain:
        raise HTTPException(status_code=400, detail="Invalid target domain")

    # Scope Authorization Check (reject unapproved active probing immediately)
    is_authorized, scope_auth_info = is_domain_in_authorized_scope(domain, db)
    if req.active_probe_allowed and not is_authorized:
        raise HTTPException(
            status_code=403,
            detail=f"Scope violation: Active probing requested for out-of-scope domain '{domain}'. Only authorized domains in the assessment inventory may be actively scanned."
        )

    # SSRF Validation on destination
    is_safe, error_msg = validate_outbound_url(req.url, allow_unresolvable=True)
    if not is_safe:
        raise HTTPException(
            status_code=400,
            detail=f"Security violation: Target destination rejected by outbound SSRF filter: {error_msg}"
        )

    # 1. Passive OSINT (DNS, TLS Cert, RDAP)
    osint_result = osint_adapter.collect_osint(domain)
    osint_data = osint_result.data
    dns_records = osint_data.get("dns", {})
    tls_info = osint_data.get("tls", {})

    # 2. Evaluate Security Headers & Cookie Policies
    header_eval = evaluate_security_headers(
        url=req.url,
        headers=req.headers or {},
        cookies=req.cookies,
        tls_info=tls_info
    )
    findings: List[SecurityFindingSchema] = header_eval["findings"]

    # 3. Technology Fingerprinting
    technologies: List[TechItemSchema] = fingerprint_technologies(
        headers=req.headers or {},
        html_content=req.html_content,
        cookies=req.cookies
    )

    # 4. CVE Vulnerability Correlation
    cve_matches: List[CVEMatchSchema] = cve_adapter.correlate_vulnerabilities(technologies)

    # 5. OWASP Top 10 Alignment
    owasp_eval = evaluate_owasp_alignment(
        url=req.url,
        headers=req.headers or {},
        findings=findings,
        technologies=technologies,
        cve_matches=cve_matches,
        html_content=req.html_content or ""
    )
    findings.extend(owasp_eval.get("extra_findings", []))

    # Recalculate score with extra OWASP findings
    severity_weights = {"CRITICAL": 35, "HIGH": 20, "MEDIUM": 10, "LOW": 4, "INFO": 0}
    cve_deductions = sum(25 if m.severity == "CRITICAL" else 15 for m in cve_matches)
    total_deductions = sum(severity_weights.get(f.severity, 0) for f in findings) + cve_deductions
    final_security_score = min(100, max(0, total_deductions))

    if final_security_score >= 80:
        level = "CRITICAL_RISK"
    elif final_security_score >= 50:
        level = "ELEVATED_RISK"
    elif final_security_score >= 20:
        level = "ACCEPTABLE"
    else:
        level = "EXCELLENT"

    latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
    assessment_id = f"sec-{uuid.uuid4().hex[:12]}"

    # Persist Assessment in Database
    db_assessment = SecurityAssessmentModel(
        id=assessment_id,
        url=req.url,
        domain=domain,
        security_score=final_security_score,
        security_level=level,
        findings_count=len(findings),
        critical_count=sum(1 for f in findings if f.severity == "CRITICAL"),
        high_count=sum(1 for f in findings if f.severity == "HIGH"),
        medium_count=sum(1 for f in findings if f.severity == "MEDIUM"),
        low_count=sum(1 for f in findings if f.severity == "LOW"),
        info_count=sum(1 for f in findings if f.severity == "INFO"),
        tech_stack=json.dumps([t.model_dump() for t in technologies]),
        cve_count=len(cve_matches),
        is_authorized_scope=is_authorized,
        dns_records=json.dumps(dns_records),
        tls_summary=json.dumps(tls_info),
        latency_ms=latency_ms
    )
    db.add(db_assessment)

    # Persist Findings
    for f in findings:
        db_finding = SecurityFindingModel(
            assessment_id=assessment_id,
            finding_id=f.finding_id,
            category=f.category,
            affected_url=f.affected_url,
            severity=f.severity,
            confidence=f.confidence,
            message=f.message,
            evidence=f.evidence,
            security_impact=f.security_impact,
            remediation=f.remediation,
            verification_status=f.verification_status
        )
        db.add(db_finding)

    # Persist CVE Matches
    for m in cve_matches:
        db_cve = CVEMatchModel(
            assessment_id=assessment_id,
            cve_id=m.cve_id,
            product=m.product,
            detected_version=m.detected_version,
            severity=m.severity,
            cvss_score=m.cvss_score,
            description=m.description,
            source=m.source,
            verification_status=m.verification_status,
            published_date=m.published_date
        )
        db.add(db_cve)

    # Auto-register asset in inventory if scope exists
    scope_obj = db.query(AssessmentScopeModel).filter(AssessmentScopeModel.domain == domain).first()
    if scope_obj:
        existing_asset = db.query(DiscoveredAssetModel).filter(
            DiscoveredAssetModel.hostname == domain
        ).first()
        if existing_asset:
            existing_asset.last_observed = datetime.datetime.now(datetime.timezone.utc)
        else:
            db_asset = DiscoveredAssetModel(
                scope_id=scope_obj.id,
                hostname=domain,
                asset_type="apex_domain",
                ip_address=dns_records.get("records", {}).get("A", [None])[0]
            )
            db.add(db_asset)

    db.commit()

    # Broadcast Live SSE Event
    event_payload = {
        "type": "SECURITY_ASSESSMENT_COMPLETED",
        "data": {
            "id": assessment_id,
            "url": req.url,
            "domain": domain,
            "security_score": final_security_score,
            "security_level": level,
            "findings_count": len(findings),
            "cve_count": len(cve_matches),
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    }
    await event_broadcaster.broadcast(event_payload)

    return SecurityAssessResponse(
        id=assessment_id,
        url=req.url,
        domain=domain,
        security_score=final_security_score,
        security_level=level,
        findings_count=len(findings),
        severity_breakdown={
            "CRITICAL": sum(1 for f in findings if f.severity == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f.severity == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f.severity == "MEDIUM"),
            "LOW": sum(1 for f in findings if f.severity == "LOW"),
            "INFO": sum(1 for f in findings if f.severity == "INFO"),
        },
        findings=findings,
        detected_technologies=technologies,
        cve_matches=cve_matches,
        dns_records=dns_records,
        tls_summary=tls_info,
        owasp_alignment=owasp_eval["categories"],
        is_authorized_scope=is_authorized,
        latency_ms=latency_ms,
        created_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/{id}")
def get_security_assessment(id: str, db: Session = Depends(get_db)):
    assessment = db.query(SecurityAssessmentModel).filter(SecurityAssessmentModel.id == id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Security assessment record not found")

    findings = db.query(SecurityFindingModel).filter(SecurityFindingModel.assessment_id == id).all()
    cves = db.query(CVEMatchModel).filter(CVEMatchModel.assessment_id == id).all()

    return {
        "id": assessment.id,
        "url": assessment.url,
        "domain": assessment.domain,
        "security_score": assessment.security_score,
        "security_level": assessment.security_level,
        "findings_count": assessment.findings_count,
        "severity_breakdown": {
            "CRITICAL": assessment.critical_count,
            "HIGH": assessment.high_count,
            "MEDIUM": assessment.medium_count,
            "LOW": assessment.low_count,
            "INFO": assessment.info_count,
        },
        "findings": [
            {
                "finding_id": f.finding_id,
                "category": f.category,
                "affected_url": f.affected_url,
                "severity": f.severity,
                "confidence": f.confidence,
                "message": f.message,
                "evidence": f.evidence,
                "security_impact": f.security_impact,
                "remediation": f.remediation,
                "verification_status": f.verification_status
            }
            for f in findings
        ],
        "technologies": json.loads(assessment.tech_stack or "[]"),
        "cve_matches": [
            {
                "cve_id": c.cve_id,
                "product": c.product,
                "detected_version": c.detected_version,
                "severity": c.severity,
                "cvss_score": c.cvss_score,
                "description": c.description,
                "source": c.source,
                "verification_status": c.verification_status
            }
            for c in cves
        ],
        "dns_records": json.loads(assessment.dns_records or "{}"),
        "tls_summary": json.loads(assessment.tls_summary or "{}"),
        "is_authorized_scope": assessment.is_authorized_scope,
        "latency_ms": assessment.latency_ms,
        "created_at": assessment.created_at.isoformat()
    }

# ============================================================================
# Security Findings Explorer
# ============================================================================

@findings_router.get("")
def list_findings(
    severity: Optional[str] = Query(None, description="Filter by severity (CRITICAL, HIGH, etc)"),
    category: Optional[str] = Query(None, description="Filter by category (headers, tls, owasp, etc)"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(SecurityFindingModel)
    if severity:
        query = query.filter(SecurityFindingModel.severity == severity.upper())
    if category:
        query = query.filter(SecurityFindingModel.category == category.lower())

    total = query.count()
    items = query.order_by(desc(SecurityFindingModel.id)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "findings": [
            {
                "id": f.id,
                "assessment_id": f.assessment_id,
                "finding_id": f.finding_id,
                "category": f.category,
                "affected_url": f.affected_url,
                "severity": f.severity,
                "confidence": f.confidence,
                "message": f.message,
                "remediation": f.remediation,
                "observed_at": f.observed_at.isoformat()
            }
            for f in items
        ]
    }

# ============================================================================
# Assessment Scope Management
# ============================================================================

@scopes_router.get("", response_model=List[ScopeResponse])
def list_scopes(db: Session = Depends(get_db)):
    scopes = db.query(AssessmentScopeModel).order_by(AssessmentScopeModel.id.desc()).all()
    return [
        ScopeResponse(
            id=s.id,
            domain=s.domain,
            description=s.description,
            is_authorized=s.is_authorized,
            authorized_by=s.authorized_by,
            created_at=s.created_at.isoformat(),
            asset_count=len(s.assets)
        )
        for s in scopes
    ]

@scopes_router.post("", response_model=ScopeResponse)
def create_scope(req: ScopeCreateRequest, db: Session = Depends(get_db)):
    scope = register_scope_domain(
        domain=req.domain,
        description=req.description or "Authorized domain assessment scope",
        authorized_by=req.authorized_by or "admin@webguard.sec",
        db=db
    )
    return ScopeResponse(
        id=scope.id,
        domain=scope.domain,
        description=scope.description,
        is_authorized=scope.is_authorized,
        authorized_by=scope.authorized_by,
        created_at=scope.created_at.isoformat(),
        asset_count=0
    )

# ============================================================================
# Attack Surface & Asset Inventory
# ============================================================================

@assets_router.get("", response_model=List[AssetResponse])
def list_assets(
    scope_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(DiscoveredAssetModel)
    if scope_id:
        query = query.filter(DiscoveredAssetModel.scope_id == scope_id)
    assets = query.order_by(desc(DiscoveredAssetModel.last_observed)).offset(offset).limit(limit).all()
    return [
        AssetResponse(
            id=a.id,
            scope_id=a.scope_id,
            hostname=a.hostname,
            asset_type=a.asset_type,
            ip_address=a.ip_address,
            cname=a.cname,
            first_observed=a.first_observed.isoformat(),
            last_observed=a.last_observed.isoformat()
        )
        for a in assets
    ]

@assets_router.post("", response_model=AssetResponse)
def add_asset(req: AssetCreateRequest, db: Session = Depends(get_db)):
    norm_host = normalize_domain(req.hostname)
    existing = db.query(DiscoveredAssetModel).filter(DiscoveredAssetModel.hostname == norm_host).first()
    if existing:
        existing.last_observed = datetime.datetime.now(datetime.timezone.utc)
        if req.ip_address:
            existing.ip_address = req.ip_address
        db.commit()
        db.refresh(existing)
        return AssetResponse(
            id=existing.id,
            scope_id=existing.scope_id,
            hostname=existing.hostname,
            asset_type=existing.asset_type,
            ip_address=existing.ip_address,
            cname=existing.cname,
            first_observed=existing.first_observed.isoformat(),
            last_observed=existing.last_observed.isoformat()
        )

    db_asset = DiscoveredAssetModel(
        scope_id=req.scope_id,
        hostname=norm_host,
        asset_type=req.asset_type,
        ip_address=req.ip_address,
        cname=req.cname
    )
    db.add(db_asset)
    db.commit()
    db.refresh(db_asset)
    return AssetResponse(
        id=db_asset.id,
        scope_id=db_asset.scope_id,
        hostname=db_asset.hostname,
        asset_type=db_asset.asset_type,
        ip_address=db_asset.ip_address,
        cname=db_asset.cname,
        first_observed=db_asset.first_observed.isoformat(),
        last_observed=db_asset.last_observed.isoformat()
    )

# ============================================================================
# Developer Security Static Code Analysis
# ============================================================================

@devsec_router.get("")
def get_developer_security_scan():
    import os
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    results = run_repository_security_scan(repo_root)
    return results
