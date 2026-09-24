"""
WebGuard ML Model Loader and Orchestrator
"""

from .price_model import price_anomaly_detector
from .review_model import review_nlp_analyzer

def get_ml_models():
    return {
        "price_detector": price_anomaly_detector,
        "review_analyzer": review_nlp_analyzer,
    }
