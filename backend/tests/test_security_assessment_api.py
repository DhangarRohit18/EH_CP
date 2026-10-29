"""
Automated Integration Tests: Technical Security Assessment API & Scope Enforcement
Tests:
- POST /api/v1/security-assessments
- GET /api/v1/security-assessments/{id}
- GET /api/v1/findings
- Scope registration & unauthorized active probe rejection (HTTP 403)
- Asset inventory management
- Provider status endpoint
- Developer security endpoint
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_and_retrieve_security_assessment():
    payload = {
        "url": "https://vulnerable-test-shop.org/products",
        "domain": "vulnerable-test-shop.org",
        "headers": {
            "Server": "Apache/2.4.49",
            "X-Powered-By": "PHP/7.4.3"
        },
        "cookies": [
            {"name": "user_session", "secure": False, "httpOnly": False}
        ],
        "html_content": "<meta name='generator' content='WordPress 5.8.1'>"
    }

    res = client.post("/api/v1/security-assessments", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert "id" in data
    assert data["id"].startswith("sec-")
    assert data["domain"] == "vulnerable-test-shop.org"
    assert data["security_score"] > 0
    assert len(data["findings"]) > 0
    assert len(data["detected_technologies"]) >= 2
    assert len(data["cve_matches"]) > 0

    # Verify retrieval from GET /api/v1/security-assessments/{id}
    assess_id = data["id"]
    get_res = client.get(f"/api/v1/security-assessments/{assess_id}")
    assert get_res.status_code == 200
    detail = get_res.json()
    assert detail["id"] == assess_id
    assert len(detail["findings"]) == len(data["findings"])

def test_active_probing_rejected_for_unauthorized_scope():
    """
    Active probing against an unapproved domain MUST be rejected with HTTP 403.
    """
    payload = {
        "url": "https://third-party-unapproved-site.com",
        "domain": "third-party-unapproved-site.com",
        "active_probe_allowed": True
    }
    res = client.post("/api/v1/security-assessments", json=payload)
    assert res.status_code == 403
    assert "Scope violation" in res.json()["detail"]

def test_findings_filtering_and_pagination():
    res = client.get("/api/v1/findings?severity=HIGH&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert "findings" in data
    assert "total" in data
    assert data["limit"] == 10

def test_scope_and_asset_inventory_management():
    # 1. Register Scope
    scope_res = client.post("/api/v1/scopes", json={
        "domain": "approved-internal-lab.net",
        "description": "Internal testbed scope",
        "authorized_by": "qa-engineer@webguard.sec"
    })
    assert scope_res.status_code == 200
    scope_data = scope_res.json()
    assert scope_data["domain"] == "approved-internal-lab.net"
    scope_id = scope_data["id"]

    # 2. Add Discovered Asset
    asset_res = client.post("/api/v1/assets", json={
        "scope_id": scope_id,
        "hostname": "api.approved-internal-lab.net",
        "asset_type": "api_endpoint",
        "ip_address": "93.184.216.34"
    })
    assert asset_res.status_code == 200
    asset_data = asset_res.json()
    assert asset_data["hostname"] == "api.approved-internal-lab.net"

    # 3. List Assets
    list_res = client.get(f"/api/v1/assets?scope_id={scope_id}")
    assert list_res.status_code == 200
    assets = list_res.json()
    assert len(assets) >= 1

def test_providers_status_endpoint():
    res = client.get("/api/providers/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "online"
    assert "domain_intel" in data["providers"]
    assert "pricing_intel" in data["providers"]
    assert "passive_osint" in data["providers"]
    assert "cve_vulnerability" in data["providers"]

def test_developer_security_endpoint():
    res = client.get("/api/v1/developer-security")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "completed"
    assert "scanned_files" in data
    assert "code_findings" in data
