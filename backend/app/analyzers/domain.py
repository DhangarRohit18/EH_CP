"""
Domain Credibility Analyzer (Weight: 20%)
Evaluates domain age, typosquatting, registrar TLD abuse, and HTTPS encryption.
"""

from typing import Dict, Any, List
from ..adapters.domain_adapter import domain_adapter

def analyze_domain(data: Dict[str, Any]) -> Dict[str, Any]:
    domain = (data.get("domain") or "").lower().strip()
    is_https = data.get("is_https", True)
    age_days = data.get("domain_age_days") # None if unavailable

    # Query domain intelligence adapter
    intel = domain_adapter.collect_domain_evidence(
        domain=domain,
        provided_age_days=age_days,
        is_https=is_https
    )

    intel_data = intel.data
    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []
    missing_evidence = intel_data.get("domain_age_days") is None

    # 1. TLS Encryption
    if not intel_data.get("is_https", True):
        raw_score += 35.0
        signals.append("Insecure connection (Plain HTTP without SSL/TLS)")
        signals_detected.append({
            "id": "domain-no-https",
            "category": "domain",
            "severity": "critical",
            "message": "Website does not enforce HTTPS encryption.",
            "rule_triggered": "RULE_DOMAIN_INSECURE_HTTP"
        })

    # 2. Domain Age
    observed_age = intel_data.get("domain_age_days")
    if observed_age is not None:
        if observed_age < 14:
            raw_score += 55.0
            signals.append(f"Domain is newly created ({observed_age} days old)")
            signals_detected.append({
                "id": "domain-age-critical",
                "category": "domain",
                "severity": "critical",
                "message": f"Domain is registered only {observed_age} days ago. Over 85% of fraudulent pop-up storefronts operate on domains under 30 days old.",
                "rule_triggered": "RULE_DOMAIN_AGE_LT_14_DAYS"
            })
        elif observed_age < 45:
            raw_score += 35.0
            signals.append(f"Relatively new domain ({observed_age} days old)")
            signals_detected.append({
                "id": "domain-age-warning",
                "category": "domain",
                "severity": "high",
                "message": f"Domain registered recently ({observed_age} days ago).",
                "rule_triggered": "RULE_DOMAIN_AGE_LT_45_DAYS"
            })
        elif observed_age > 730:
            raw_score = max(5.0, raw_score - 15.0)
            signals.append(f"Established domain with {observed_age // 365}+ years history")
    else:
        signals.append("Domain registration age could not be confirmed")

    # 3. High-Abuse TLD
    if intel_data.get("is_suspicious_tld"):
        raw_score += 25.0
        signals.append("Domain utilizes high-abuse disposable TLD extension")
        signals_detected.append({
            "id": "domain-suspicious-tld",
            "category": "domain",
            "severity": "high",
            "message": "Top-Level Domain (TLD) matches known high-abuse registrar categories.",
            "rule_triggered": "RULE_HIGH_ABUSE_TLD"
        })

    # 4. Brand Mimicry & Typosquatting
    mimicry = intel_data.get("brand_mimicry")
    if mimicry:
        raw_score += mimicry.get("points", 40.0)
        signals.append(mimicry["message"])
        signals_detected.append({
            "id": "domain-typosquat",
            "category": "domain",
            "severity": mimicry.get("severity", "critical"),
            "message": mimicry["message"],
            "rule_triggered": "RULE_TYPOSQUAT_BRAND_MIMIC"
        })

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "confidence": intel.confidence,
        "missing_evidence": missing_evidence,
        "reason": signals[0] if signals else "Domain attributes verified within normal limits.",
        "signals": signals,
        "detected_signals": signals_detected
    }
