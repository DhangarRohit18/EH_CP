"""
Integration Tests: FastAPI REST Endpoints & Database Persistence
Tests Analysis submission, SQLAlchemy ORM writes, History filtering, and Transactional Deletion.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    # Ensure fresh schema
    Base.metadata.create_all(bind=engine)
    yield

def test_health_check_endpoint():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("online", "degraded")
    assert data["database"]["status"] == "connected"
    assert "ml_inference" in data
    assert data["ml_inference"]["isolation_forest_ready"] is True

def test_analyze_storefront_and_persistence():
    payload = {
        "url": "https://test-scam-shop.top/deal",
        "domain": "test-scam-shop.top",
        "product_name": "Apple iPhone 16 Pro",
        "price": 19999.0,
        "reference_market_price": 119999.0,
        "is_https": False,
        "domain_age_days": 5,
        "refund_policy_text": "All sales final no returns",
        "payment_methods": ["Personal UPI QR Only"],
        "reviews": [
            "Best phone ever received original product within 1 day awesome quality!",
            "Best phone ever received original product within 1 day awesome quality!",
            "Best phone ever received original product within 1 day awesome quality!"
        ],
        "has_countdown_timer": True,
        "is_iframe_checkout": True
    }

    res = client.post("/api/v1/analyze", json=payload)
    assert res.status_code == 200
    data = res.json()

    # Validate output schema fields
    assert "id" in data
    assert data["risk_score"] >= 80
    assert data["risk_level"] == "CRITICAL"
    assert data["is_pre_payment_triggered"] is True
    assert len(data["factors"]) == 7
    assert len(data["detected_signals"]) >= 3

    analysis_id = data["id"]

    # Verify retrieval from GET /api/v1/history/{id}
    detail_res = client.get(f"/api/v1/history/{analysis_id}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["id"] == analysis_id
    assert detail["domain"] == "test-scam-shop.top"
    assert len(detail["factors"]) == 7

def test_history_filtering_and_pagination():
    # Insert two distinct records
    client.post("/api/v1/analyze", json={
        "url": "https://trusted-merchant.com",
        "domain": "trusted-merchant.com",
        "price": 5000.0,
        "reference_market_price": 5200.0,
        "domain_age_days": 800,
        "is_https": True,
        "contact_email": "support@trusted-merchant.com",
        "refund_policy_text": "30 days full refund guaranteed",
        "payment_methods": ["Razorpay", "Visa"]
    })

    client.post("/api/v1/analyze", json={
        "url": "https://wild-trap.xyz",
        "domain": "wild-trap.xyz",
        "price": 999.0,
        "reference_market_price": 15000.0,
        "domain_age_days": 3,
        "is_https": False,
        "payment_methods": ["Prepaid Only"]
    })

    # Filter by domain
    dom_res = client.get("/api/v1/history?domain=trusted-merchant")
    assert dom_res.status_code == 200
    items = dom_res.json()
    assert all("trusted-merchant" in item["domain"] for item in items)

    # Filter by risk level
    crit_res = client.get("/api/v1/history?risk_level=CRITICAL")
    assert crit_res.status_code == 200
    crit_items = crit_res.json()
    assert all(item["risk_level"] == "CRITICAL" for item in crit_items)

def test_history_deletion():
    # Post record
    post_res = client.post("/api/v1/analyze", json={
        "url": "https://delete-target.shop",
        "domain": "delete-target.shop"
    })
    analysis_id = post_res.json()["id"]

    # Delete single record
    del_res = client.delete(f"/api/v1/history/{analysis_id}")
    assert del_res.status_code == 200

    # Ensure 404 on subsequent get
    check_res = client.get(f"/api/v1/history/{analysis_id}")
    assert check_res.status_code == 404

    # Clear all history
    clear_res = client.delete("/api/v1/history")
    assert clear_res.status_code == 200
    empty_history = client.get("/api/v1/history")
    assert empty_history.status_code == 200
    assert len(empty_history.json()) == 0
