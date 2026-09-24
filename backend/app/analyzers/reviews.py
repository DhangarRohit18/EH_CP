"""
Review Patterns Analyzer (Weight: 15%)
Uses NLP to detect duplicate reviews, synthetic phrasing, and rating skew.
"""

from typing import Dict, Any, List
from ..ml.review_model import review_nlp_analyzer

def analyze_reviews(data: Dict[str, Any]) -> Dict[str, Any]:
    raw_reviews = data.get("reviews") or []
    texts = [r.get("text", "") for r in raw_reviews if isinstance(r, dict)]
    ratings = [float(r.get("rating", 5.0)) for r in raw_reviews if isinstance(r, dict)]

    nlp_result = review_nlp_analyzer.analyze_reviews(texts, ratings)
    signals_detected: List[Dict[str, Any]] = []

    if nlp_result["has_duplicates"]:
        signals_detected.append({
            "id": "reviews-synthesized",
            "category": "reviews",
            "severity": "high",
            "message": "NLP text feature analysis detected synthetic duplicate phrasing and review uniformity.",
            "rule_triggered": "RULE_REVIEW_NLP_DUPLICATES_DETECTED"
        })

    return {
        "score": nlp_result["risk_score"],
        "similarity_score": nlp_result["similarity_score"],
        "reason": "Multiple reviews contain similar wording." if nlp_result["has_duplicates"] else nlp_result["reason"],
        "signals": [nlp_result["reason"]],
        "detected_signals": signals_detected
    }
