"""
Payment Methods Analyzer (Weight: 10%)
Flags prepaid-only demands, personal UPI VPAs, and lack of trusted escrow gateways.
IMPORTANT: Never captures, handles, or stores sensitive payment credentials.
"""

from typing import Dict, Any, List

def analyze_payment(data: Dict[str, Any]) -> Dict[str, Any]:
    methods = [m.lower() for m in (data.get("payment_methods") or [])]

    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    has_prepaid_only = any("prepaid only" in m or "advance only" in m for m in methods)
    has_personal_upi = any("personal upi" in m or "@okhdfcbank" in m or "@okaxis" in m or "paytm-merchant" in m for m in methods)
    has_wire = any("bank transfer" in m or "crypto" in m or "western union" in m for m in methods)
    has_trusted = any("razorpay" in m or "stripe" in m or "paypal" in m or "visa" in m or "mastercard" in m for m in methods)
    has_cod = any("cash on delivery" in m or "cod" in m for m in methods)

    if has_prepaid_only or has_personal_upi or has_wire:
        raw_score = 95.0
        if has_prepaid_only:
            signals.append("Website primarily requests prepaid payment.")
        if has_personal_upi:
            signals.append("Requests direct transfer to personal unverified UPI handle.")
        if has_wire:
            signals.append("Enforces irreversible wire or crypto payment.")
        signals_detected.append({
            "id": "payment-prepaid-only",
            "category": "payment",
            "severity": "critical",
            "message": "Payment checkout forces non-reversible payment rails without buyer protection.",
            "rule_triggered": "RULE_PAYMENT_IRREVERSIBLE_RAILS"
        })
    elif not has_trusted and not has_cod:
        raw_score = 60.0
        signals.append("Unverified checkout payment gateway.")
    else:
        raw_score = 5.0
        signals.append("Certified secure payment gateway with buyer protection detected.")

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "reason": signals[0] if signals else "Payment gateway verified.",
        "signals": signals,
        "detected_signals": signals_detected
    }
