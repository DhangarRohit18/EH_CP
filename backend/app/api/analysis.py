"""
Analysis API Router
Endpoint: POST /api/v1/analyze
Canonical Single Source of Truth for E-Commerce Fraud Risk Evaluation
"""

import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.analysis import (
    AnalyzeRequest,
    AnalyzeResponse,
    Analysis,
    FactorResultModel,
    DetectedSignalModel,
    EvidenceRecordModel,
    DomainProfileModel,
)
from ..database import get_db
from ..engine.risk_engine import compute_risk
from .events import broadcaster

router = APIRouter(prefix="/analyze", tags=["Analysis"])

@router.post("", response_model=AnalyzeResponse)
async def analyze_storefront(request: AnalyzeRequest, db: Session = Depends(get_db)):
    payload_dict = request.model_dump()
    result = compute_risk(payload_dict)

    # 1. Transactional Database Persistence
    try:
        db_analysis = Analysis(
            id=result["id"],
            url=result["url"],
            domain=result["domain"],
            normalized_domain=result["normalized_domain"],
            product_name=result.get("product_name"),
            price=result.get("price"),
            currency=result.get("currency", "₹"),
            risk_score=result["risk_score"],
            risk_level=result["risk_level"],
            evidence_coverage=result.get("evidence_coverage", 1.0),
            latency_ms=result.get("latency_ms", 0.0),
            model_version=result.get("metadata", {}).get("model_version", "v1.2.0"),
            recommendation=result.get("recommendation"),
            is_pre_payment_triggered=result.get("is_pre_payment_triggered", False)
        )
        db.add(db_analysis)

        # Persist Factors
        for f_key, f_val in result["factors"].items():
            db_factor = FactorResultModel(
                analysis_id=result["id"],
                factor_name=f_key,
                raw_score=f_val["raw_score"],
                weight=f_val["weight"],
                contribution=f_val["contribution"],
                confidence=f_val.get("confidence", 1.0),
                status=f_val.get("status", "safe"),
                explanation=f_val["reason"],
                missing_evidence=f_val.get("missing_evidence", False)
            )
            db.add(db_factor)

        # Persist Detected Signals
        for sig in result["detected_signals"]:
            db_sig = DetectedSignalModel(
                analysis_id=result["id"],
                category=sig["category"],
                severity=sig["severity"],
                message=sig["message"],
                rule_triggered=sig.get("rule_triggered")
            )
            db.add(db_sig)

        # Upsert Domain Profile
        norm_dom = result["normalized_domain"]
        domain_profile = db.query(DomainProfileModel).filter(DomainProfileModel.domain == norm_dom).first()
        if domain_profile:
            domain_profile.last_seen = datetime.datetime.now(datetime.timezone.utc)
            domain_profile.scan_count += 1
            domain_profile.last_risk_score = result["risk_score"]
            domain_profile.avg_risk_score = round(
                (domain_profile.avg_risk_score * (domain_profile.scan_count - 1) + result["risk_score"]) / domain_profile.scan_count,
                1
            )
        else:
            domain_profile = DomainProfileModel(
                domain=norm_dom,
                registrable_domain=norm_dom,
                last_risk_score=result["risk_score"],
                avg_risk_score=float(result["risk_score"]),
                scan_count=1
            )
            db.add(domain_profile)

        db.commit()
    except Exception as e:
        db.rollback()
        # Log error cleanly without crashing evaluation
        print(f"[WebGuard Database Persistence Error] {e}")

    # 2. Broadcast Event to Live Telemetry SSE Stream
    try:
        await broadcaster.broadcast("analysis_completed", {
            "id": result["id"],
            "domain": result["domain"],
            "product_name": result.get("product_name"),
            "risk_score": result["risk_score"],
            "risk_level": result["risk_level"],
            "is_pre_payment_triggered": result.get("is_pre_payment_triggered", False),
            "latency_ms": result.get("latency_ms", 0.0),
            "timestamp": result["timestamp"]
        })
    except Exception as be:
        print(f"[WebGuard SSE Broadcast Warning] {be}")

    return result
