"""
Price Anomaly Analyzer (Weight: 20%)
Calculates discount percentage and triggers Isolation Forest anomaly detector.
"""

from typing import Dict, Any, List
from ..ml.price_model import price_anomaly_detector

def analyze_price(data: Dict[str, Any]) -> Dict[str, Any]:
    listed_price = float(data.get("price") or 0.0)
    ref_price = float(data.get("reference_market_price") or data.get("original_price") or listed_price)
    currency = data.get("currency", "₹")

    discount_pct = 0.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    if ref_price > 0 and listed_price > 0 and listed_price < ref_price:
        discount_pct = round(((ref_price - listed_price) / ref_price) * 100.0, 1)

    is_anomaly, ml_score = price_anomaly_detector.predict_anomaly(discount_pct)

    if discount_pct >= 75.0:
        signals.append("Product is significantly below expected market price.")
        signals_detected.append({
            "id": "price-anomaly-critical",
            "category": "price",
            "severity": "critical",
            "message": f"Product is priced at {currency}{listed_price:,.0f} vs market benchmark {currency}{ref_price:,.0f} ({discount_pct}% discount). Classic bait pricing indicator.",
            "rule_triggered": "RULE_PRICE_DISCOUNT_GT_75"
        })
    elif discount_pct >= 50.0:
        signals.append(f"Unusually steep discount of {discount_pct}% detected.")
        signals_detected.append({
            "id": "price-anomaly-high",
            "category": "price",
            "severity": "high",
            "message": f"Suspiciously high price reduction of {discount_pct}%.",
            "rule_triggered": "RULE_PRICE_DISCOUNT_GT_50"
        })
    else:
        signals.append("Pricing is consistent with standard retail competition.")

    return {
        "score": ml_score,
        "discount_pct": discount_pct,
        "is_anomaly": is_anomaly,
        "reason": signals[0] if signals else "Price conforms to retail norms.",
        "signals": signals,
        "detected_signals": signals_detected
    }
