"""
Automated Test Suite: 6 Controlled Storefront Evaluation Fixtures
Master Prompt Section 13:
- Fixture A: Normal store with ordinary pricing and complete metadata
- Fixture B: Suspicious store with newly registered domain, steep discount, repeated reviews, risky payment
- Fixture C: Store with missing metadata
- Fixture D: Store where external intelligence providers time out / trip circuit breaker
- Fixture E: Store with dynamic price or checkout content
- Fixture F: Store with misleading hostnames and typosquatting / brand mimicry
"""

import pytest
from app.engine.risk_engine import compute_risk
from app.adapters.price_adapter import PriceEvidenceAdapter
from app.adapters.domain_adapter import DomainIntelligenceAdapter
from app.adapters.base import ProviderStatus
from app.engine.thresholds import (
    RISK_LEVEL_LOW,
    RISK_LEVEL_MEDIUM,
    RISK_LEVEL_HIGH,
    RISK_LEVEL_CRITICAL,
    PRE_PAYMENT_INTERCEPT_THRESHOLD
)

def test_storefront_fixture_a_normal_legitimate_store():
    """
    Storefront A: Legitimate, long-standing domain, realistic pricing, verified payment gateways,
    legitimate refund policy, diverse reviews, and clear merchant identity.
    Expected: LOW risk (0-29).
    """
    payload = {
        "url": "https://www.croma.com/apple-iphone-16-pro-128gb/p/308942",
        "domain": "www.croma.com",
        "product_name": "Apple iPhone 16 Pro 128GB",
        "price": 114900.0,
        "original_price": 119900.0,
        "reference_market_price": 119900.0,
        "is_https": True,
        "domain_age_days": 4200,
        "contact_email": "customersupport@croma.com",
        "contact_phone": "+91-1800-269-3333",
        "company_address": "Tata Digital Private Limited, Mumbai, Maharashtra, India",
        "refund_policy_text": "Standard 7-day replacement warranty for manufacturing defects. Official brand center support.",
        "payment_methods": ["Visa", "Mastercard", "NetBanking", "UPI (Official Gateway)", "EMI"],
        "reviews": [
            "Delivery took 2 days. The titanium finish looks great and battery backup is solid.",
            "Upgraded from iPhone 13. Camera action button is surprisingly convenient.",
            "Display is gorgeous. Slightly heavy in hand but performance is stellar."
        ],
        "is_checkout_page": False
    }

    result = compute_risk(payload)
    assert result["risk_score"] < 30, f"Expected LOW risk for legitimate store, got {result['risk_score']}"
    assert result["risk_level"] == RISK_LEVEL_LOW
    assert result["is_pre_payment_triggered"] is False
    assert result["evidence_coverage"] >= 0.85
    assert result["factors"]["domain"]["raw_score"] <= 20
    assert result["factors"]["price"]["raw_score"] <= 20

def test_storefront_fixture_b_suspicious_scam_store():
    """
    Storefront B: Newly registered domain, 85% discount on high-demand electronics,
    identical duplicate reviews, prepaid UPI QR only, no refund policy.
    Expected: CRITICAL risk (>= 80), pre-payment intercept triggered.
    """
    payload = {
        "url": "https://super-mega-discounts-india.shop/deal/iphone16pro",
        "domain": "super-mega-discounts-india.shop",
        "product_name": "Apple iPhone 16 Pro 128GB",
        "price": 14999.0,
        "original_price": 119900.0,
        "reference_market_price": 119900.0,
        "is_https": False,
        "domain_age_days": 4,
        "refund_policy_text": "No refunds no cancellations all sales final.",
        "payment_methods": ["Direct UPI transfer to private personal number"],
        "reviews": [
            "Best phone ever received original in 24 hours amazing seller!",
            "Best phone ever received original in 24 hours amazing seller!",
            "Best phone ever received original in 24 hours amazing seller!"
        ],
        "behaviour_signals": ["fake_countdown_timer", "disabled_right_click"],
        "is_checkout_page": False
    }

    result = compute_risk(payload)
    assert result["risk_score"] >= 80, f"Expected CRITICAL risk for blatant scam, got {result['risk_score']}"
    assert result["risk_level"] == RISK_LEVEL_CRITICAL
    assert result["is_pre_payment_triggered"] is True
    assert len(result["detected_signals"]) >= 3
    # Verify specific signals were surfaced
    signal_rules = [s["rule_triggered"] for s in result["detected_signals"]]
    assert "RULE_DOMAIN_AGE_LT_14_DAYS" in signal_rules
    assert "RULE_PRICE_DISCOUNT_GT_75" in signal_rules

def test_storefront_fixture_c_missing_metadata_store():
    """
    Storefront C: Store where price reference is missing and contact info is unavailable.
    Evidence coverage is lower, missing evidence is disclosed, and no fake data is fabricated.
    """
    payload = {
        "url": "https://unknown-artisan-crafts.org/item/handmade-bowl",
        "domain": "unknown-artisan-crafts.org",
        "product_name": "Handmade Clay Bowl",
        "price": 1200.0,
        "is_https": True,
        "domain_age_days": 180,
        # Contact info missing, reviews missing, reference market price missing
        "payment_methods": ["Cash on Delivery", "Razorpay"],
        "refund_policy_text": "Returns accepted within 14 days in original condition."
    }

    result = compute_risk(payload)
    assert result["evidence_coverage"] < 1.0
    # Price factor must be marked as missing reference evidence
    assert result["factors"]["price"]["missing_evidence"] is True
    assert "Missing baseline" in result["factors"]["price"]["reason"] or "unavailable" in result["factors"]["price"]["reason"].lower()
    # Review factor must note missing reviews
    assert result["factors"]["reviews"]["missing_evidence"] is True
    assert result["risk_score"] <= 60 # Not falsely marked CRITICAL when only elements are missing

def test_storefront_fixture_d_provider_circuit_breaker_and_timeout():
    """
    Storefront D: External intelligence providers time out or fail.
    The adapter returns UNAVAILABLE or ERROR with circuit breaker tripped.
    The risk engine operates safely without crashing.
    """
    price_adapter = PriceEvidenceAdapter()
    
    # Simulate consecutive failures to trip circuit breaker
    price_adapter.circuit_breaker.record_failure()
    price_adapter.circuit_breaker.record_failure()
    price_adapter.circuit_breaker.record_failure()
    assert price_adapter.circuit_breaker.state == "OPEN"

    # Adapter call should immediately return UNAVAILABLE without network hang
    res = price_adapter.evaluate_pricing("Any Product", 500.0)
    assert res.status == ProviderStatus.UNAVAILABLE
    assert "Circuit breaker active" in res.error_message

    # Compute risk with provider degraded
    payload = {
        "url": "https://example-shop.in/product",
        "domain": "example-shop.in",
        "price": 500.0,
        "is_https": True,
        "domain_age_days": 200
    }
    result = compute_risk(payload)
    assert result["risk_score"] >= 0
    assert result["risk_score"] <= 100

def test_storefront_fixture_e_dynamic_price_and_checkout_intercept():
    """
    Storefront E: Store where page is at checkout stage.
    When is_checkout_page is True, even moderate risk triggers pre-payment advisory warning.
    """
    # Moderate risk item (55 risk points) on browsing page -> no pre-payment trigger
    browse_payload = {
        "url": "https://new-outlet-sale.in/item",
        "domain": "new-outlet-sale.in",
        "product_name": "Running Shoes",
        "price": 2000.0,
        "reference_market_price": 5000.0, # 60% discount
        "domain_age_days": 25, # young domain
        "is_https": True,
        "is_checkout_page": False
    }
    browse_res = compute_risk(browse_payload)
    assert browse_res["risk_score"] >= 30
    assert browse_res["is_pre_payment_triggered"] is False

    # Same storefront, but now entering payment/checkout stage
    checkout_payload = {**browse_payload, "is_checkout_page": True}
    checkout_res = compute_risk(checkout_payload)
    assert checkout_res["is_pre_payment_triggered"] is True
    assert "checkout" in checkout_res["recommendation"].lower()

def test_storefront_fixture_f_typosquatting_and_brand_mimicry():
    """
    Storefront F: Misleading hostnames designed to impersonate trusted brands.
    Examples: 'amaz0n-security.com', 'flipk4rt-deals.shop'.
    Expected: Strong brand mimicry signals detected, domain factor risk >= 60.
    """
    payload = {
        "url": "https://amaz0n-prime-special.in/cart",
        "domain": "amaz0n-prime-special.in",
        "product_name": "Sony WH-1000XM5 Headphones",
        "price": 8999.0,
        "reference_market_price": 29990.0,
        "domain_age_days": 10,
        "is_https": True,
        "payment_methods": ["Personal UPI Only"]
    }

    result = compute_risk(payload)
    assert result["factors"]["domain"]["raw_score"] >= 60
    assert result["risk_score"] >= 60
    
    # Verify typosquatting signal was raised
    signal_rules = [s["rule_triggered"] for s in result["detected_signals"]]
    assert "RULE_TYPOSQUAT_BRAND_MIMIC" in signal_rules
