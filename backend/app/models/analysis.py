"""
WebGuard Unified Database Models & Pydantic Data Contracts
Canonical Source of Truth for Analysis, Persistence, and Audit Trail
"""

import datetime
import json
from typing import List, Optional, Dict, Any, Union
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean, Index
)
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field, field_validator
from ..database import Base

# ============================================================================
# SQLAlchemy ORM Models
# ============================================================================

def utc_now():
    return datetime.datetime.now(datetime.timezone.utc)

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String(64), primary_key=True, index=True)
    url = Column(String(2048), nullable=False, index=True)
    domain = Column(String(255), nullable=False, index=True)
    normalized_domain = Column(String(255), nullable=False, index=True)
    product_name = Column(String(512), nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String(16), default="₹")
    risk_score = Column(Integer, nullable=False, index=True)
    risk_level = Column(String(32), nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    evidence_coverage = Column(Float, default=1.0) # 0.0 - 1.0 proportion of factors with valid evidence
    latency_ms = Column(Float, default=0.0)
    model_version = Column(String(64), default="v1.2.0")
    recommendation = Column(Text, nullable=True)
    is_pre_payment_triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now, index=True)

    factors = relationship("FactorResultModel", back_populates="analysis", cascade="all, delete-orphan")
    signals = relationship("DetectedSignalModel", back_populates="analysis", cascade="all, delete-orphan")
    evidence_records = relationship("EvidenceRecordModel", back_populates="analysis", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_domain_created", "domain", "created_at"),
        Index("idx_risk_created", "risk_level", "created_at"),
    )


class FactorResultModel(Base):
    __tablename__ = "factor_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(64), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    factor_name = Column(String(64), nullable=False) # domain, price, reviews, identity, policy, payment, behaviour
    raw_score = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    contribution = Column(Integer, nullable=False)
    confidence = Column(Float, default=1.0) # 0.0 - 1.0
    status = Column(String(32), default="safe") # safe, warning, danger, unavailable
    explanation = Column(Text, nullable=False)
    missing_evidence = Column(Boolean, default=False)

    analysis = relationship("Analysis", back_populates="factors")


class DetectedSignalModel(Base):
    __tablename__ = "detected_signals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(64), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(64), nullable=False)
    severity = Column(String(32), nullable=False) # low, medium, high, critical
    message = Column(Text, nullable=False)
    rule_triggered = Column(String(128), nullable=True)

    analysis = relationship("Analysis", back_populates="signals")


class EvidenceRecordModel(Base):
    __tablename__ = "evidence_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String(64), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    provider_name = Column(String(64), nullable=False) # browser_dom, dns_whois, market_pricing, nlp_reviews
    evidence_type = Column(String(64), nullable=False) # domain_age, price_deviation, duplicate_reviews, payment_gateway
    status = Column(String(32), default="SUCCESS") # SUCCESS, UNAVAILABLE, STALE, RATE_LIMITED, ERROR
    confidence = Column(Float, default=1.0)
    raw_data = Column(Text, nullable=True) # JSON serialized evidence metadata
    retrieved_at = Column(DateTime, default=utc_now)

    analysis = relationship("Analysis", back_populates="evidence_records")


class DomainProfileModel(Base):
    __tablename__ = "domain_profiles"

    domain = Column(String(255), primary_key=True, index=True)
    registrable_domain = Column(String(255), nullable=False, index=True)
    first_seen = Column(DateTime, default=utc_now)
    last_seen = Column(DateTime, default=utc_now)
    scan_count = Column(Integer, default=1)
    last_risk_score = Column(Integer, default=0)
    avg_risk_score = Column(Float, default=0.0)


# ============================================================================
# Pydantic v2 Request & Response Schemas
# ============================================================================

class ReviewItem(BaseModel):
    author: Optional[str] = None
    text: str
    rating: Optional[float] = 5.0
    date: Optional[str] = None


class AnalyzeRequest(BaseModel):
    url: str = Field(..., max_length=2048, description="Target storefront URL")
    domain: str = Field(..., max_length=255, description="Target storefront hostname")
    product_name: Optional[str] = Field(None, max_length=512)
    price: Optional[float] = Field(None, ge=0.0)
    currency: Optional[str] = Field("₹", max_length=16)
    original_price: Optional[float] = Field(None, ge=0.0)
    reference_market_price: Optional[float] = Field(None, ge=0.0)
    reviews: Optional[List[Union[ReviewItem, str]]] = Field(default_factory=list)
    rating: Optional[float] = Field(None, ge=0.0, le=5.0)
    review_count: Optional[int] = Field(None, ge=0)
    refund_policy_text: Optional[str] = Field(None, max_length=10000)
    payment_methods: Optional[List[str]] = Field(default_factory=list)
    contact_email: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=64)
    company_address: Optional[str] = Field(None, max_length=512)
    is_https: Optional[bool] = True
    domain_age_days: Optional[int] = None # None means external lookup needed
    has_suspicious_redirects: Optional[bool] = False
    has_hidden_forms: Optional[bool] = False
    has_countdown_timer: Optional[bool] = False
    is_iframe_checkout: Optional[bool] = False
    behaviour_signals: Optional[List[str]] = Field(default_factory=list)
    is_checkout_page: Optional[bool] = False

    @field_validator("reviews", mode="before")
    @classmethod
    def normalize_reviews(cls, v):
        if not v:
            return []
        normalized = []
        for item in v:
            if isinstance(item, str):
                normalized.append(ReviewItem(text=item))
            elif isinstance(item, dict):
                normalized.append(ReviewItem(**item))
            else:
                normalized.append(item)
        return normalized

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: str) -> str:
        clean = v.strip()
        if not (clean.startswith("http://") or clean.startswith("https://")):
            clean = "https://" + clean
        return clean

    @field_validator("domain")
    @classmethod
    def validate_domain_name(cls, v: str) -> str:
        clean = v.strip().lower()
        # Remove any protocol or path if accidentally passed
        clean = clean.replace("http://", "").replace("https://", "").split("/")[0]
        return clean


class FactorScoreSchema(BaseModel):
    name: str
    raw_score: float
    weight: float
    contribution: int
    confidence: float = 1.0
    reason: str
    sub_signals: Optional[List[str]] = Field(default_factory=list)
    status: str # safe, warning, danger, unavailable
    missing_evidence: bool = False


class FactorsSchema(BaseModel):
    domain: FactorScoreSchema
    price: FactorScoreSchema
    reviews: FactorScoreSchema
    identity: FactorScoreSchema
    policy: FactorScoreSchema
    payment: FactorScoreSchema
    behaviour: FactorScoreSchema


class SignalSchema(BaseModel):
    id: str
    category: str
    severity: str
    message: str
    rule_triggered: Optional[str] = None


class ExplanationSchema(BaseModel):
    factor: str
    points: int
    explanation: str
    weight_percent: int
    severity: str


class EvidenceItemSchema(BaseModel):
    provider_name: str
    evidence_type: str
    status: str
    confidence: float
    retrieved_at: str
    data: Optional[Dict[str, Any]] = None


class AnalyzeResponse(BaseModel):
    id: str
    url: str
    domain: str
    normalized_domain: str
    product_name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "₹"
    risk_score: int
    risk_level: str
    evidence_coverage: float
    latency_ms: float
    factors: FactorsSchema
    explanations: List[ExplanationSchema]
    detected_signals: List[SignalSchema]
    evidence_summary: Optional[List[EvidenceItemSchema]] = Field(default_factory=list)
    recommendation: str
    timestamp: str
    is_pre_payment_triggered: bool
    metadata: Optional[Dict[str, Any]] = None


class HistoryItemSchema(BaseModel):
    id: str
    url: str
    domain: str
    product_name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "₹"
    risk_score: int
    risk_level: str
    evidence_coverage: float
    latency_ms: float
    created_at: str
    top_reasons: List[str]
    is_pre_payment_triggered: bool


class HistoryListResponse(BaseModel):
    total: int
    items: List[HistoryItemSchema]
