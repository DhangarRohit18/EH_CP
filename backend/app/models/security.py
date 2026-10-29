"""
WebGuard Technical Security Models & Pydantic Data Contracts
Canonical Source of Truth for Technical Security Assessments, OWASP Findings,
Asset Inventory, and CVE Intelligence.
"""

import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, field_validator
from ..database import Base

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================

class AssessmentScopeModel(Base):
    __tablename__ = "assessment_scopes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(String(512), nullable=True)
    is_authorized = Column(Boolean, default=True)
    authorized_by = Column(String(128), default="admin@webguard.sec")
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=True)

    assets = relationship("DiscoveredAssetModel", back_populates="scope", cascade="all, delete-orphan")


class DiscoveredAssetModel(Base):
    __tablename__ = "discovered_assets"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scope_id = Column(Integer, ForeignKey("assessment_scopes.id", ondelete="CASCADE"), nullable=True, index=True)
    hostname = Column(String(255), nullable=False, index=True)
    asset_type = Column(String(64), default="subdomain") # apex_domain, subdomain, api_endpoint
    ip_address = Column(String(64), nullable=True)
    cname = Column(String(255), nullable=True)
    detected_services = Column(Text, nullable=True) # JSON list
    first_observed = Column(DateTime, default=utc_now)
    last_observed = Column(DateTime, default=utc_now)

    scope = relationship("AssessmentScopeModel", back_populates="assets")


class SecurityAssessmentModel(Base):
    __tablename__ = "security_assessments"

    id = Column(String(64), primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    security_score = Column(Integer, nullable=False, index=True) # 0 to 100
    security_level = Column(String(32), nullable=False, index=True) # EXCELLENT, ACCEPTABLE, ELEVATED_RISK, CRITICAL_RISK
    findings_count = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    info_count = Column(Integer, default=0)
    tech_stack = Column(Text, nullable=True) # JSON serialized
    cve_count = Column(Integer, default=0)
    is_authorized_scope = Column(Boolean, default=False)
    dns_records = Column(Text, nullable=True) # JSON serialized
    tls_summary = Column(Text, nullable=True) # JSON serialized
    latency_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now, index=True)

    findings = relationship("SecurityFindingModel", back_populates="assessment", cascade="all, delete-orphan")
    cve_matches = relationship("CVEMatchModel", back_populates="assessment", cascade="all, delete-orphan")


class SecurityFindingModel(Base):
    __tablename__ = "security_findings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_id = Column(String(64), ForeignKey("security_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    finding_id = Column(String(64), nullable=False, index=True) # e.g. SEC-HDR-NO-CSP
    category = Column(String(64), nullable=False, index=True) # headers, tls, cookies, owasp, redirects, dns
    affected_url = Column(String(2048), nullable=False)
    severity = Column(String(32), nullable=False, index=True) # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence = Column(Float, default=1.0) # 0.0 - 1.0
    message = Column(Text, nullable=False)
    evidence = Column(Text, nullable=True)
    security_impact = Column(Text, nullable=True)
    remediation = Column(Text, nullable=True)
    verification_status = Column(String(32), default="verified") # verified, potential, informational
    observed_at = Column(DateTime, default=utc_now)

    assessment = relationship("SecurityAssessmentModel", back_populates="findings")


class CVEMatchModel(Base):
    __tablename__ = "cve_matches"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    assessment_id = Column(String(64), ForeignKey("security_assessments.id", ondelete="CASCADE"), nullable=False, index=True)
    cve_id = Column(String(32), nullable=False, index=True) # e.g. CVE-2023-3824
    product = Column(String(128), nullable=False)
    detected_version = Column(String(64), nullable=True)
    severity = Column(String(32), default="MEDIUM")
    cvss_score = Column(Float, default=5.0)
    description = Column(Text, nullable=False)
    source = Column(String(64), default="NVD/NIST")
    verification_status = Column(String(32), default="potentially_affected") # potentially_affected vs verified
    published_date = Column(String(32), nullable=True)

    assessment = relationship("SecurityAssessmentModel", back_populates="cve_matches")


# ============================================================================
# Pydantic v2 Schemas
# ============================================================================

class SecurityFindingSchema(BaseModel):
    finding_id: str
    category: str
    affected_url: str
    severity: str
    confidence: float = 1.0
    message: str
    evidence: Optional[str] = None
    security_impact: Optional[str] = None
    remediation: Optional[str] = None
    verification_status: str = "verified"


class CVEMatchSchema(BaseModel):
    cve_id: str
    product: str
    detected_version: Optional[str] = None
    severity: str
    cvss_score: float
    description: str
    source: str = "NVD/NIST"
    verification_status: str = "potentially_affected"
    published_date: Optional[str] = None


class TechItemSchema(BaseModel):
    name: str
    category: str # web_server, cms, framework, cdn, analytics
    version: Optional[str] = None
    confidence: float = 1.0
    evidence: str


class SecurityAssessRequest(BaseModel):
    url: str = Field(..., max_length=2048, description="Target website URL")
    domain: Optional[str] = Field(None, max_length=255)
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="Observable public HTTP response headers")
    cookies: Optional[List[Dict[str, Any]]] = Field(default_factory=list, description="Observable cookie flags (HttpOnly, Secure, SameSite)")
    html_content: Optional[str] = Field(None, description="Public HTML head for metadata & script tag inspection")
    active_probe_allowed: Optional[bool] = Field(False, description="Whether target is an authorized lab for active probes")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://")):
            clean = "https://" + clean
        return clean


class SecurityAssessResponse(BaseModel):
    id: str
    url: str
    domain: str
    security_score: int # 0 (pristine) to 100 (critical issues)
    security_level: str # EXCELLENT, ACCEPTABLE, ELEVATED_RISK, CRITICAL_RISK
    findings_count: int
    severity_breakdown: Dict[str, int]
    findings: List[SecurityFindingSchema]
    detected_technologies: List[TechItemSchema]
    cve_matches: List[CVEMatchSchema]
    dns_records: Dict[str, Any]
    tls_summary: Dict[str, Any]
    owasp_alignment: Dict[str, Any]
    is_authorized_scope: bool
    latency_ms: float
    created_at: str


class ScopeCreateRequest(BaseModel):
    domain: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=512)
    authorized_by: Optional[str] = Field("admin@webguard.sec", max_length=128)
    is_authorized: Optional[bool] = True


class ScopeResponse(BaseModel):
    id: int
    domain: str
    description: Optional[str]
    is_authorized: bool
    authorized_by: str
    created_at: str
    asset_count: int = 0


class AssetCreateRequest(BaseModel):
    scope_id: Optional[int] = None
    hostname: str = Field(..., max_length=255)
    asset_type: str = Field("subdomain", max_length=64)
    ip_address: Optional[str] = Field(None, max_length=64)
    cname: Optional[str] = Field(None, max_length=255)


class AssetResponse(BaseModel):
    id: int
    scope_id: Optional[int]
    hostname: str
    asset_type: str
    ip_address: Optional[str]
    cname: Optional[str]
    first_observed: str
    last_observed: str
