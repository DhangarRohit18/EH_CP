"""
Automated Unit Tests: WebGuard Core Risk Engine & Thresholds
Verifies all 7 factors, mathematical boundaries, missing evidence, and absence of hardcoded hacks.
"""

import pytest
from app.engine.risk_engine import compute_risk
from app.engine.thresholds import (
    WEIGHTS,
    get_risk_level,
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    PRE_PAYMENT_INTERCEPT_THRESHOLD,
)
from app.utils.domain_parser import normalize_domain, detect_brand_mimicry, parse_registrable_domain

def test_weights_sum_to_exact_100_percent():
    total_weight = sum(WEIGHTS.values())
    assert abs(total_weight - 1.0) < 1e-6, f"Weights must strictly sum to 1.00 (got {total_weight})"
    assert len(WEIGHTS) == 7, "Must contain exactly seven operational fraud factors"

def test_risk_level_threshold_boundaries():
    assert get_risk_level(0) == RISK_LEVEL_LOW
    assert get_risk_level(29) == RISK_LEVEL_LOW
    assert get_risk_level(30) == RISK_LEVEL_MEDIUM
    assert get_risk_level(59) == RISK_LEVEL_MEDIUM
    assert get_risk_level(60) == RISK_LEVEL_HIGH
    assert get_risk_level(79) == RISK_LEVEL_HIGH
    assert get_risk_level(80) == RISK_LEVEL_CRITICAL
    assert get_risk_level(100) == RISK_LEVEL_CRITICAL

def test_deterministic_scoring_output():
    payload = {
        "url": "https://sample-storefront.com/item",
        "domain": "sample-storefront.com",
        "product_name": "Leather Shoes",
        "price": 2500.0,
        "reference_market_price": 2800.0,
        "is_https": True,
        "domain_age_days": 400,
        "contact_email": "support@sample-storefront.com",
        "contact_phone": "+91-9876543210",
        "refund_policy_text": "30-day no hassle returns and exchanges available for all customers.",
        "payment_methods": ["Razorpay", "Visa", "Mastercard", "Cash on Delivery"]
    }

    res1 = compute_risk(payload)
    res2 = compute_risk(payload)

    assert res1["risk_score"] == res2["risk_score"]
    assert res1["risk_level"] == res2["risk_level"]
    assert res1["factors"]["domain"]["contribution"] == res2["factors"]["domain"]["contribution"]
    assert res1["factors"]["price"]["contribution"] == res2["factors"]["price"]["contribution"]

def test_no_hardcoded_domain_demo_overrides():
    """
    Changing the domain name of the demo scenario MUST NOT trigger hardcoded score overrides.
    Scores must be derived purely from the payload evidence.
    """
    evidence_base = {
        "product_name": "Apple iPhone 16 Pro 256GB",
        "price": 24999.0,
        "reference_market_price": 119999.0, # 79% discount
        "is_https": True,
        "domain_age_days": 8, # <14 days critical
        "reviews": [
            {"author": "User A", "text": "Great product arrived in 2 days, best price ever!", "rating": 5.0},
            {"author": "User B", "text": "Great product arrived in 2 days, best price ever!", "rating": 5.0},
        ],
        "contact_email": "deals.support@gmail.com", # Free email
        "refund_policy_text": "All sales final. 24h window with 35% restocking fee.",
        "payment_methods": ["Prepaid Only", "Personal UPI QR"]
    }

    # Case 1: flashdeal-electronics.local
    res_canonical = compute_risk({**evidence_base, "url": "https://flashdeal-electronics.local", "domain": "flashdeal-electronics.local"})

    # Case 2: arbitrary-scam-store.xyz with identical evidence
    res_arbitrary = compute_risk({**evidence_base, "url": "https://arbitrary-scam-store.xyz", "domain": "arbitrary-scam-store.xyz"})

    # Both must evaluate evidence objectively into high/critical fraud risk without arbitrary special-case overrides
    assert res_canonical["risk_score"] >= PRE_PAYMENT_INTERCEPT_THRESHOLD
    assert res_arbitrary["risk_score"] >= PRE_PAYMENT_INTERCEPT_THRESHOLD
    assert res_canonical["is_pre_payment_triggered"] is True
    assert res_arbitrary["is_pre_payment_triggered"] is True

def test_missing_price_evidence_lowers_coverage():
    """
    When reference pricing is absent, the engine must lower evidence coverage
    and transparently disclose that price risk could not be fully evaluated.
    """
    payload = {
        "url": "https://obscure-boutique.com/art",
        "domain": "obscure-boutique.com",
        "product_name": "Custom Handcrafted Vase",
        "price": 1200.0,
        # reference_market_price is omitted
    }

    res = compute_risk(payload)
    assert res["factors"]["price"]["missing_evidence"] is True
    assert "unavailable" in res["factors"]["price"]["reason"].lower()
    assert res["evidence_coverage"] < 1.0

def test_domain_lookalikes_and_typosquatting():
    # Subdomain spoofing
    sub_spoof = detect_brand_mimicry("amazon.com.fake-store-checkout.org")
    assert sub_spoof is not None
    assert sub_spoof["type"] == "subdomain_spoofing"

    # Typosquatting
    typo = detect_brand_mimicry("amazn.shop")
    assert typo is not None
    assert typo["type"] == "typosquatting"

    # Legitimate domain
    legit = detect_brand_mimicry("amazon.com")
    assert legit is None

def test_all_seven_factors_bounded():
    payload = {
        "url": "https://random-store.com",
        "domain": "random-store.com",
        "price": 100.0,
    }
    res = compute_risk(payload)
    assert 0 <= res["risk_score"] <= 100
    for key, f in res["factors"].items():
        assert 0.0 <= f["raw_score"] <= 100.0
        assert f["contribution"] >= 0
        assert f["status"] in ("safe", "warning", "danger")
