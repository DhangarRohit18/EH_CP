"""
Website Identity Analyzer (Weight: 15%)
Validates merchant contact email, corporate phone, and physical address.
"""

from typing import Dict, Any, List

def analyze_identity(data: Dict[str, Any]) -> Dict[str, Any]:
    email = data.get("contact_email") or ""
    phone = data.get("contact_phone") or ""
    address = data.get("company_address") or ""

    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    is_free_email = any(f in email.lower() for f in ["gmail.com", "hotmail.com", "yahoo.com", "proton.me"])

    if not email and not phone:
        raw_score += 45.0
        signals.append("Merchant lacks verifiable contact email and phone support.")
        signals_detected.append({
            "id": "identity-no-contact",
            "category": "identity",
            "severity": "high",
            "message": "Merchant does not list verifiable direct support phone or corporate email.",
            "rule_triggered": "RULE_IDENTITY_MISSING_CONTACT"
        })
    elif is_free_email:
        raw_score += 30.0
        signals.append(f"Merchant relies on generic free webmail ({email}).")
        signals_detected.append({
            "id": "identity-free-email",
            "category": "identity",
            "severity": "medium",
            "message": f"Support contact uses free public email host ({email}) rather than official corporate domain.",
            "rule_triggered": "RULE_IDENTITY_FREE_WEBMAIL"
        })

    if not address:
        raw_score += 15.0
        signals.append("No physical business address listed.")

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "reason": signals[0] if signals else "Merchant corporate contact identity verified.",
        "signals": signals,
        "detected_signals": signals_detected
    }
