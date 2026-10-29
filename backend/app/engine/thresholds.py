"""
WebGuard Centralized Thresholds, Factor Weights, and Classification Engine
Single Source of Truth across Backend, Extension, and Frontend
"""

from typing import Dict

# ============================================================================
# Exact Factor Weights (Must sum strictly to 1.00 / 100%)
# ============================================================================
WEIGHTS: Dict[str, float] = {
    "domain": 0.20,
    "price": 0.20,
    "reviews": 0.15,
    "identity": 0.15,
    "policy": 0.10,
    "payment": 0.10,
    "behaviour": 0.10,
}

assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "Factor weights must sum strictly to 100%"

# ============================================================================
# Standard Risk Tiers
# ============================================================================
RISK_LEVEL_LOW = "LOW"          # 0 - 29 (Safe to proceed)
RISK_LEVEL_MEDIUM = "MEDIUM"    # 30 - 59 (Exercise caution)
RISK_LEVEL_HIGH = "HIGH"        # 60 - 79 (Warning overlay triggered)
RISK_LEVEL_CRITICAL = "CRITICAL"# 80 - 100 (Critical fraud risk / imminent loss)

def get_risk_level(score: int) -> str:
    """
    Centralized mapping of numerical score to risk tier.
    """
    if score >= 80:
        return RISK_LEVEL_CRITICAL
    elif score >= 60:
        return RISK_LEVEL_HIGH
    elif score >= 30:
        return RISK_LEVEL_MEDIUM
    return RISK_LEVEL_LOW

# Pre-payment warning threshold:
# When score >= 60 or on checkout with high deception indicators
PRE_PAYMENT_INTERCEPT_THRESHOLD = 60

# ============================================================================
# High-Abuse TLD Categories (Frequently used by ephemeral fraud storefronts)
# ============================================================================
SUSPICIOUS_TLDS = [
    ".top", ".xyz", ".buzz", ".icu", ".club", ".shop", ".click",
    ".live", ".work", ".vip", ".rest", ".fit", ".monster", ".online", ".store"
]

# ============================================================================
# Established Brand Benchmarks for Typosquatting / Lookalike Detection
# ============================================================================
BRAND_BENCHMARKS = [
    "amazon", "flipkart", "apple", "walmart", "target", "bestbuy",
    "ebay", "myntra", "croma", "reliancedigital", "tatacliq", "nike",
    "adidas", "samsung", "zara", "shein", "meesho"
]
