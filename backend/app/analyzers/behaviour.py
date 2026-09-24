"""
Site Behaviour Analyzer (Weight: 10%)
Detects suspicious redirects, hidden DOM inputs, and artificial psychological pressure triggers.
"""

from typing import Dict, Any, List

def analyze_behaviour(data: Dict[str, Any]) -> Dict[str, Any]:
    has_redirects = bool(data.get("has_suspicious_redirects", False))
    has_hidden = bool(data.get("has_hidden_forms", False))
    custom_signals = data.get("behaviour_signals") or []

    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    if has_redirects:
        raw_score += 45.0
        signals.append("Suspicious navigation behaviour detected.")
        signals_detected.append({
            "id": "behaviour-redirect",
            "category": "behaviour",
            "severity": "high",
            "message": "Checkout button attempts to redirect to an unaffiliated foreign payment domain.",
            "rule_triggered": "RULE_BEHAVIOUR_SUSPICIOUS_REDIRECT"
        })

    if has_hidden:
        raw_score += 25.0
        signals.append("Hidden DOM form elements or obfuscated input collectors detected.")
        signals_detected.append({
            "id": "behaviour-hidden-forms",
            "category": "behaviour",
            "severity": "medium",
            "message": "Underlying DOM tree contains off-screen hidden input collectors.",
            "rule_triggered": "RULE_BEHAVIOUR_HIDDEN_FORM"
        })

    for s in custom_signals:
        raw_score += 15.0
        signals.append(s)

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "reason": signals[0] if signals else "Standard site navigation and DOM structure verified.",
        "signals": signals,
        "detected_signals": signals_detected
    }
