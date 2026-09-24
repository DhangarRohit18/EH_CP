import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field
from ..database import Base

# ==========================================
# SQLAlchemy ORM Models
# ==========================================

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)
    url = Column(String, index=True)
    domain = Column(String, index=True)
    product_name = Column(String, nullable=True)
    price = Column(Float, nullable=True)
    currency = Column(String, default="₹")
    risk_score = Column(Integer, index=True)
    risk_level = Column(String, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    recommendation = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    factors = relationship("FactorResultModel", back_populates="analysis", cascade="all, delete-orphan")
    signals = relationship("DetectedSignalModel", back_populates="analysis", cascade="all, delete-orphan")


class FactorResultModel(Base):
    __tablename__ = "factor_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    factor_name = Column(String) # domain, price, reviews, identity, policy, payment, behaviour
    raw_score = Column(Float)
    weight = Column(Float)
    contribution = Column(Integer)
    explanation = Column(Text)

    analysis = relationship("Analysis", back_populates="factors")


class DetectedSignalModel(Base):
    __tablename__ = "detected_signals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(String, ForeignKey("analyses.id"))
    category = Column(String)
    severity = Column(String) # low, medium, high, critical
    message = Column(Text)
    rule_triggered = Column(String, nullable=True)

    analysis = relationship("Analysis", back_populates="signals")


# ==========================================
# Pydantic Request & Response Contracts
# ==========================================

class ReviewItem(BaseModel):
    author: Optional[str] = None
    text: str
    rating: Optional[float] = 5.0
    date: Optional[str] = None


class AnalyzeRequest(BaseModel):
    url: str
    domain: str
    product_name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "₹"
    original_price: Optional[float] = None
    reference_market_price: Optional[float] = None
    reviews: Optional[List[ReviewItem]] = Field(default_factory=list)
    rating: Optional[float] = None
    review_count: Optional[int] = None
    refund_policy: Optional[str] = None
    refund_policy_text: Optional[str] = None
    payment_methods: Optional[List[str]] = Field(default_factory=list)
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    company_address: Optional[str] = None
    is_https: Optional[bool] = True
    domain_age_days: Optional[int] = 365
    has_suspicious_redirects: Optional[bool] = False
    has_hidden_forms: Optional[bool] = False
    behaviour_signals: Optional[List[str]] = Field(default_factory=list)
    is_checkout_page: Optional[bool] = False


class FactorScoreSchema(BaseModel):
    name: str
    raw_score: float
    weight: float
    contribution: int
    reason: str
    sub_signals: Optional[List[str]] = Field(default_factory=list)
    status: str


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


class AnalyzeResponse(BaseModel):
    id: str
    url: str
    domain: str
    product_name: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = "₹"
    risk_score: int
    risk_level: str
    factors: FactorsSchema
    explanations: List[ExplanationSchema]
    detected_signals: List[SignalSchema]
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
    created_at: str
    top_reasons: List[str]
