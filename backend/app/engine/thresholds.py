"""
Thresholds, Weights, and Constants for WebGuard Multi-Factor Risk Engine
"""

WEIGHTS = {
    "domain": 0.20,
    "price": 0.20,
    "reviews": 0.15,
    "identity": 0.15,
    "policy": 0.10,
    "payment": 0.10,
    "behaviour": 0.10,
}

# Verify weights sum exactly to 1.0 (100%)
assert abs(sum(WEIGHTS.values()) - 1.0) < 1e-6, "Weights must sum to 100%"

RISK_LEVEL_LOW = "LOW"
RISK_LEVEL_MEDIUM = "MEDIUM"
RISK_LEVEL_HIGH = "HIGH"
RISK_LEVEL_CRITICAL = "CRITICAL"

POPULAR_DOMAINS = [
    "amazon.com", "amazon.in", "flipkart.com", "apple.com", "walmart.com",
    "bestbuy.com", "target.com", "ebay.com", "myntra.com", "tatacliq.com",
    "nike.com", "adidas.com", "samsung.com", "croma.com", "reliancedigital.in"
]

SUSPICIOUS_TLDS = [
    ".top", ".xyz", ".buzz", ".icu", ".club", ".shop", ".click", ".live", ".work", ".vip", ".rest"
]
