"""
WebGuard Core Risk Engine (Single Source of Truth)
Evaluates 7 distinct operational fraud factors from real evidence with additive explainability.
Weights (Strictly sum to 1.00 / 100%):
- Domain Credibility: 20%
- Price Anomaly:      20%
- Review Patterns:    15%
- Website Identity:   15%
- Refund Policy:      10%
- Payment Methods:    10%
- Site Behaviour:     10%
"""

import time
import uuid
import datetime
from typing import Dict, Any, List
from .thresholds import (
    WEIGHTS,
    get_risk_level,
    PRE_PAYMENT_INTERCEPT_THRESHOLD,
)
from .explainability import generate_explanations
from ..utils.domain_parser import normalize_domain
from ..analyzers.domain import analyze_domain
from ..analyzers.price import analyze_price
from ..analyzers.reviews import analyze_reviews
from ..analyzers.identity import analyze_identity
from ..analyzers.policy import analyze_policy
from ..analyzers.payment import analyze_payment
from ..analyzers.behaviour import analyze_behaviour

def compute_risk(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes evidence-backed composite risk score and factor decomposition.
    No hardcoded domain overrides or simulated numbers.
    """
    start_time = time.perf_counter()
    url = payload.get("url", "").strip()
    raw_domain = payload.get("domain", "").strip()
    norm_domain = normalize_domain(raw_domain or url)
    payload["domain"] = norm_domain

    # 1. Run 7 Operational Factor Analyzers
    d_res = analyze_domain(payload)
    pr_res = analyze_price(payload)
    rv_res = analyze_reviews(payload)
    id_res = analyze_identity(payload)
    pol_res = analyze_policy(payload)
    pay_res = analyze_payment(payload)
    beh_res = analyze_behaviour(payload)

    # 2. Collect Detected Signals
    detected_signals: List[Dict[str, Any]] = (
        d_res["detected_signals"] +
        pr_res["detected_signals"] +
        rv_res["detected_signals"] +
        id_res["detected_signals"] +
        pol_res["detected_signals"] +
        pay_res["detected_signals"] +
        beh_res["detected_signals"]
    )

    # 3. Additive Weighted Contributions
    domain_contrib = int(round(d_res["score"] * WEIGHTS["domain"]))
    price_contrib = int(round(pr_res["score"] * WEIGHTS["price"]))
    review_contrib = int(round(rv_res["score"] * WEIGHTS["reviews"]))
    identity_contrib = int(round(id_res["score"] * WEIGHTS["identity"]))
    policy_contrib = int(round(pol_res["score"] * WEIGHTS["policy"]))
    payment_contrib = int(round(pay_res["score"] * WEIGHTS["payment"]))
    behaviour_contrib = int(round(beh_res["score"] * WEIGHTS["behaviour"]))

    total_score = min(
        100,
        max(0, (
            domain_contrib +
            price_contrib +
            review_contrib +
            identity_contrib +
            policy_contrib +
            payment_contrib +
            behaviour_contrib
        ))
    )

    # 4. Evidence Coverage Ratio
    analyzers_evidence = [
        not d_res.get("missing_evidence", False),
        not pr_res.get("missing_evidence", False),
        not rv_res.get("missing_evidence", False),
        bool(payload.get("contact_email") or payload.get("contact_phone")),
        bool(payload.get("refund_policy_text") or payload.get("refund_policy")),
        bool(payload.get("payment_methods")),
        True, # Behavior observer active
    ]
    evidence_coverage = round(sum(1 for v in analyzers_evidence if v) / len(analyzers_evidence), 2)

    # 5. Risk Tier Determination
    risk_level = get_risk_level(total_score)
    is_checkout = bool(payload.get("is_checkout_page", False))
    is_pre_payment_triggered = (
        total_score >= PRE_PAYMENT_INTERCEPT_THRESHOLD or
        (is_checkout and total_score >= 50)
    )

    # 6. Structured Factors
    factors = {
        "domain": {
            "name": "Domain Credibility",
            "raw_score": d_res["score"],
            "weight": WEIGHTS["domain"],
            "contribution": domain_contrib,
            "confidence": d_res.get("confidence", 1.0),
            "missing_evidence": d_res.get("missing_evidence", False),
            "reason": d_res["reason"],
            "sub_signals": d_res.get("signals", []),
            "status": "danger" if d_res["score"] > 50 else ("warning" if d_res["score"] > 25 else "safe")
        },
        "price": {
            "name": "Price Anomaly",
            "raw_score": pr_res["score"],
            "weight": WEIGHTS["price"],
            "contribution": price_contrib,
            "confidence": pr_res.get("confidence", 1.0),
            "missing_evidence": pr_res.get("missing_evidence", False),
            "reason": pr_res["reason"],
            "sub_signals": pr_res.get("signals", []),
            "status": "danger" if pr_res["score"] > 50 else ("warning" if pr_res["score"] > 25 else "safe")
        },
        "reviews": {
            "name": "Review Patterns",
            "raw_score": rv_res["score"],
            "weight": WEIGHTS["reviews"],
            "contribution": review_contrib,
            "confidence": rv_res.get("confidence", 1.0),
            "missing_evidence": rv_res.get("missing_evidence", False),
            "reason": rv_res["reason"],
            "sub_signals": rv_res.get("signals", []),
            "status": "danger" if rv_res["score"] > 50 else ("warning" if rv_res["score"] > 25 else "safe")
        },
        "identity": {
            "name": "Website Identity",
            "raw_score": id_res["score"],
            "weight": WEIGHTS["identity"],
            "contribution": identity_contrib,
            "confidence": 0.90,
            "missing_evidence": not bool(payload.get("contact_email") or payload.get("contact_phone")),
            "reason": id_res["reason"],
            "sub_signals": id_res.get("signals", []),
            "status": "danger" if id_res["score"] > 50 else ("warning" if id_res["score"] > 25 else "safe")
        },
        "policy": {
            "name": "Refund Policy",
            "raw_score": pol_res["score"],
            "weight": WEIGHTS["policy"],
            "contribution": policy_contrib,
            "confidence": 0.95,
            "missing_evidence": not bool(payload.get("refund_policy_text") or payload.get("refund_policy")),
            "reason": pol_res["reason"],
            "sub_signals": pol_res.get("signals", []),
            "status": "danger" if pol_res["score"] > 50 else ("warning" if pol_res["score"] > 25 else "safe")
        },
        "payment": {
            "name": "Payment Methods",
            "raw_score": pay_res["score"],
            "weight": WEIGHTS["payment"],
            "contribution": payment_contrib,
            "confidence": 0.95,
            "missing_evidence": not bool(payload.get("payment_methods")),
            "reason": pay_res["reason"],
            "sub_signals": pay_res.get("signals", []),
            "status": "danger" if pay_res["score"] > 50 else ("warning" if pay_res["score"] > 25 else "safe")
        },
        "behaviour": {
            "name": "Site Behaviour",
            "raw_score": beh_res["score"],
            "weight": WEIGHTS["behaviour"],
            "contribution": behaviour_contrib,
            "confidence": 0.85,
            "missing_evidence": False,
            "reason": beh_res["reason"],
            "sub_signals": beh_res.get("signals", []),
            "status": "danger" if beh_res["score"] > 50 else ("warning" if beh_res["score"] > 25 else "safe")
        }
    }

    # 7. Dynamic Evidence-Mapped Recommendations
    recommendations = []
    if payment_contrib >= 6:
        recommendations.append("Do not transfer money to unverified personal UPI handles or advance wire traps.")
    if price_contrib >= 10:
        recommendations.append("Verify the product price from authenticated retail benchmarks; discount is statistically anomalous.")
    if domain_contrib >= 8:
        recommendations.append("Verify the merchant's official domain name and look for typosquatting variations.")
    if policy_contrib >= 6:
        recommendations.append("Review return and refund terms; merchant fails to provide transparent buyer protections.")
    if is_checkout and total_score >= 30:
        recommendations.insert(0, "Advisory pre-payment warning: checkout phase detected with elevated risk indicators. Pause and verify merchant authenticity before entering payment details.")

    if not recommendations:
        if total_score >= 60:
            recommendations.append("Exercise extreme caution before entering payment credentials.")
        else:
            recommendations.append("Standard e-commerce indicators observed. Proceed with normal purchasing caution.")

    recommendation_text = " ".join(recommendations)

    # 8. Measure Actual Execution Latency
    latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

    return {
        "id": f"scan-{uuid.uuid4().hex[:12]}",
        "url": url,
        "domain": raw_domain,
        "normalized_domain": norm_domain,
        "product_name": payload.get("product_name"),
        "price": payload.get("price"),
        "currency": payload.get("currency", "₹"),
        "risk_score": total_score,
        "risk_level": risk_level,
        "evidence_coverage": evidence_coverage,
        "latency_ms": latency_ms,
        "factors": factors,
        "explanations": generate_explanations(factors),
        "detected_signals": detected_signals,
        "recommendation": recommendation_text,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "is_pre_payment_triggered": is_pre_payment_triggered,
        "metadata": {
            "model_version": "v1.2.0",
            "scoring_rule": "additive_weighted_evidence_model",
            "isolation_forest_active": not pr_res.get("missing_evidence", False),
            "nlp_similarity_score": rv_res.get("similarity_score", 0.0),
            "evidence_coverage_pct": int(evidence_coverage * 100),
            "latency_ms": latency_ms,
        }
    }
