"""
Health Check API Router
Endpoint: GET /api/v1/health
"""

import datetime
from fastapi import APIRouter
from ..ml.model_loader import get_ml_models

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check():
    ml_models = get_ml_models()
    price_ready = ml_models["price_detector"].is_trained
    return {
        "status": "online",
        "service": "WebGuard Fraud Risk Engine",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "ml_models": {
            "isolation_forest_loaded": price_ready,
            "nlp_review_analyzer_loaded": True
        },
        "weights_configured": {
            "domain": 0.20,
            "price": 0.20,
            "reviews": 0.15,
            "identity": 0.15,
            "policy": 0.10,
            "payment": 0.10,
            "behaviour": 0.10,
            "total": 1.00
        }
    }
