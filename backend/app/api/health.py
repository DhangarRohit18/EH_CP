"""
Health & Readiness Check API Router
Endpoint: GET /api/v1/health
"""

import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from ..ml.model_loader import get_ml_models
from ..adapters.domain_adapter import domain_adapter
from ..adapters.price_adapter import price_adapter
from ..engine.thresholds import WEIGHTS

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    # Check Database connection
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)[:100]}"

    # Check ML Models
    ml_models = get_ml_models()
    price_ready = ml_models["price_detector"].is_trained
    nlp_ready = ml_models["review_analyzer"].vectorizer is not None

    # Check Providers Circuit Breakers
    domain_breaker = domain_adapter.circuit_breaker.state
    price_breaker = price_adapter.circuit_breaker.state

    return {
        "status": "online" if db_status == "connected" else "degraded",
        "service": "WebGuard Fraud Risk Assessment Engine",
        "version": "1.2.0",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "database": {
            "status": db_status,
            "engine": "sqlite" if "sqlite" in str(db.bind.url) else "postgresql"
        },
        "ml_inference": {
            "isolation_forest_ready": price_ready,
            "isolation_forest_version": ml_models["price_detector"].model_version,
            "review_nlp_tfidf_ready": nlp_ready,
            "review_nlp_version": ml_models["review_analyzer"].model_version
        },
        "providers": {
            "domain_intelligence": {"circuit_breaker": domain_breaker},
            "pricing_intelligence": {"circuit_breaker": price_breaker}
        },
        "weights": WEIGHTS
    }
