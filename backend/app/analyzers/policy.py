"""
Refund Policy Analyzer (Weight: 10%)
Analyzes return policy presence, timeline clarity, and restrictive clauses.
"""

from typing import Dict, Any, List

def analyze_policy(data: Dict[str, Any]) -> Dict[str, Any]:
    text = (data.get("refund_policy_text") or data.get("refund_policy") or "").lower().strip()

    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    if not text:
        raw_score = 95.0
        signals.append("Refund information is completely missing.")
        signals_detected.append({
            "id": "policy-missing",
            "category": "policy",
            "severity": "critical",
            "message": "Website fails to provide a legally required return or refund policy document.",
            "rule_triggered": "RULE_REFUND_POLICY_ABSENT"
        })
    elif "no refund" in text or "all sales final" in text:
        raw_score = 85.0
        signals.append("Strict 'no returns / all sales final' restrictive policy enforced.")
        signals_detected.append({
            "id": "policy-no-return",
            "category": "policy",
            "severity": "high",
            "message": "Merchant explicitly disallows refunds, chargebacks, or product returns.",
            "rule_triggered": "RULE_REFUND_POLICY_STRICT_NO_RETURNS"
        })
    elif len(text) < 120 or "day" not in text:
        raw_score = 75.0
        signals.append("Refund information is incomplete.")
        signals_detected.append({
            "id": "policy-vague",
            "category": "policy",
            "severity": "medium",
            "message": "Refund clause lacks specified return window or reverse logistics instructions.",
            "rule_triggered": "RULE_REFUND_POLICY_INCOMPLETE"
        })
    else:
        raw_score = 5.0
        signals.append("Standard return window and claims process verified.")

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "reason": signals[0] if signals else "Clear refund policy verified.",
        "signals": signals,
        "detected_signals": signals_detected
    }
