"""
Review Patterns Analyzer (Weight: 15%)
Uses NLP TF-IDF cosine similarity to detect duplicate reviews, synthetic phrasing, and rating skew.
"""

from typing import Dict, Any, List
from ..ml.review_model import review_nlp_analyzer

def analyze_reviews(data: Dict[str, Any]) -> Dict[str, Any]:
    raw_reviews = data.get("reviews") or []
    texts = [r.strip() if isinstance(r, str) else r.get("text", "").strip() for r in raw_reviews]
    texts = [t for t in texts if t]
    ratings = [5.0 if isinstance(r, str) else float(r.get("rating", 5.0)) for r in raw_reviews]

    nlp_result = review_nlp_analyzer.analyze_reviews(texts, ratings)
    signals_detected: List[Dict[str, Any]] = []
    missing_evidence = len(texts) == 0

    if nlp_result["has_duplicates"]:
        signals_detected.append({
            "id": "reviews-synthesized",
            "category": "reviews",
            "severity": "critical" if nlp_result["similarity_score"] >= 0.85 else "high",
            "message": f"NLP text analysis identified synthetic duplicate review phrasing (cosine similarity: {nlp_result['similarity_score']:.2f}, {nlp_result['duplicate_count']} duplicates).",
            "rule_triggered": "RULE_REVIEW_NLP_DUPLICATES_DETECTED"
        })
    elif missing_evidence:
        signals_detected.append({
            "id": "reviews-none",
            "category": "reviews",
            "severity": "medium",
            "message": "No customer reviews available on the listing to assess authentic user feedback.",
            "rule_triggered": "RULE_REVIEWS_EMPTY"
        })

    return {
        "score": nlp_result["risk_score"],
        "confidence": nlp_result["confidence"],
        "missing_evidence": missing_evidence,
        "sample_size": nlp_result["sample_size"],
        "similarity_score": nlp_result["similarity_score"],
        "reason": nlp_result["reason"],
        "signals": [nlp_result["reason"]],
        "detected_signals": signals_detected
    }
