"""
Price Anomaly Analyzer (Weight: 20%)
Calculates discount deviation and runs Scikit-Learn Isolation Forest anomaly detector.
"""

from typing import Dict, Any, List
from ..adapters.price_adapter import price_adapter
from ..ml.price_model import price_anomaly_detector

def analyze_price(data: Dict[str, Any]) -> Dict[str, Any]:
    product_name = data.get("product_name")
    observed_price = data.get("price")
    currency = data.get("currency", "₹")
    ref_price = data.get("reference_market_price")
    orig_price = data.get("original_price")

    price_evidence = price_adapter.evaluate_pricing(
        product_name=product_name,
        observed_price=observed_price,
        currency=currency,
        provided_ref_price=ref_price,
        provided_orig_price=orig_price
    )

    pdata = price_evidence.data
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    if not pdata.get("is_evaluated"):
        # Missing price benchmark evidence
        return {
            "score": 15.0, # Neutral baseline
            "discount_pct": 0.0,
            "is_anomaly": False,
            "confidence": price_evidence.confidence,
            "missing_evidence": True,
            "reason": "Reference market pricing unavailable for comparison. Price risk could not be fully evaluated.",
            "signals": ["Market benchmark reference price not available"],
            "detected_signals": []
        }

    discount_pct = float(pdata.get("discount_pct", 0.0))
    is_anomaly, ml_score, ml_meta = price_anomaly_detector.predict_anomaly(discount_pct)

    benchmark_val = pdata.get("reference_price", 0.0)
    source_desc = pdata.get("reference_source", "market benchmark")

    if discount_pct >= 75.0:
        signals.append(f"Extreme price deviation: {discount_pct}% below {source_desc}")
        signals_detected.append({
            "id": "price-anomaly-critical",
            "category": "price",
            "severity": "critical",
            "message": f"Product offered at {currency}{observed_price:,.0f} vs authenticated benchmark {currency}{benchmark_val:,.0f} ({discount_pct}% off). Isolation Forest flagged as high-confidence outlier.",
            "rule_triggered": "RULE_PRICE_DISCOUNT_GT_75"
        })
    elif discount_pct >= 50.0:
        signals.append(f"Unusually steep discount of {discount_pct}% off benchmark")
        signals_detected.append({
            "id": "price-anomaly-high",
            "category": "price",
            "severity": "high",
            "message": f"Suspiciously steep reduction of {discount_pct}% below authenticated retail price.",
            "rule_triggered": "RULE_PRICE_DISCOUNT_GT_50"
        })
    elif discount_pct >= 30.0:
        signals.append(f"Moderate promotional discount ({discount_pct}%)")
    else:
        signals.append("Pricing is consistent with standard competitive retail")

    return {
        "score": ml_score,
        "discount_pct": discount_pct,
        "is_anomaly": is_anomaly,
        "confidence": price_evidence.confidence,
        "missing_evidence": False,
        "reason": signals[0] if signals else "Price conforms to retail norms.",
        "signals": signals,
        "detected_signals": signals_detected,
        "metadata": ml_meta
    }
