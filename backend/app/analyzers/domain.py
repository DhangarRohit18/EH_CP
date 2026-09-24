"""
Domain Credibility Analyzer (Weight: 20%)
Evaluates domain age, typosquatting, suspicious TLDs, and HTTPS configuration.
"""

from typing import Dict, Any, List
from ..engine.thresholds import POPULAR_DOMAINS, SUSPICIOUS_TLDS

def analyze_domain(data: Dict[str, Any]) -> Dict[str, Any]:
    domain = (data.get("domain") or "").lower().strip()
    is_https = data.get("is_https", True)
    age_days = data.get("domain_age_days", 365)
    
    raw_score = 10.0
    signals: List[str] = []
    signals_detected: List[Dict[str, Any]] = []

    # 1. TLS/HTTPS
    if not is_https:
        raw_score += 35.0
        signals.append("Insecure HTTP connection")
        signals_detected.append({
            "id": "domain-no-https",
            "category": "domain",
            "severity": "critical",
            "message": "Website does not enforce HTTPS encryption.",
            "rule_triggered": "RULE_DOMAIN_INSECURE_HTTP"
        })

    # 2. Domain Age
    if age_days < 14:
        raw_score += 55.0
        signals.append(f"Domain appears recently registered ({age_days} days ago)")
        signals_detected.append({
            "id": "domain-age-critical",
            "category": "domain",
            "severity": "critical",
            "message": f"Domain registered only {age_days} days ago. High correlation with ephemeral scam stores.",
            "rule_triggered": "RULE_DOMAIN_AGE_LT_14_DAYS"
        })
    elif age_days < 45:
        raw_score += 35.0
        signals.append(f"Domain registered {age_days} days ago")
    elif age_days > 730:
        raw_score = max(0.0, raw_score - 20.0)
        signals.append("Domain has established operational history (>2 years)")

    # 3. High-Abuse TLD
    has_suspicious_tld = any(domain.endswith(tld) for tld in SUSPICIOUS_TLDS)
    if has_suspicious_tld:
        raw_score += 25.0
        signals.append("Domain utilizes high-abuse disposable TLD extension")
        signals_detected.append({
            "id": "domain-suspicious-tld",
            "category": "domain",
            "severity": "high",
            "message": "Top-Level Domain (TLD) matches known high-abuse registrar categories.",
            "rule_triggered": "RULE_HIGH_ABUSE_TLD"
        })

    # 4. Typosquatting / Impersonation
    for pop in POPULAR_DOMAINS:
        clean_pop = pop.split(".")[0]
        if clean_pop in domain and not domain.endswith(pop):
            raw_score += 40.0
            signals.append(f"Possible typosquatting / brand mimicry of '{clean_pop}'")
            signals_detected.append({
                "id": "domain-typosquat",
                "category": "domain",
                "severity": "critical",
                "message": f"Domain appears to mimic established marketplace '{pop}'.",
                "rule_triggered": "RULE_TYPOSQUAT_BRAND_MIMIC"
            })
            break

    final_score = min(100.0, max(0.0, raw_score))
    return {
        "score": final_score,
        "reason": signals[0] if signals else "Domain attributes verified within normal limits.",
        "signals": signals,
        "detected_signals": signals_detected
    }
