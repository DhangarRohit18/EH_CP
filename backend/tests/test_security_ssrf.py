"""
Automated Test Suite: WebGuard SSRF Protection & Network Security
Validates outbound destination sanitization, RFC1918 blocking, cloud metadata defense,
and DNS resolution verification.
"""

import pytest
from app.utils.security import is_ip_allowed, validate_outbound_url

def test_loopback_and_localhost_blocked():
    assert is_ip_allowed("127.0.0.1") is False
    assert is_ip_allowed("127.0.1.1") is False
    assert is_ip_allowed("::1") is False
    
    valid, reason = validate_outbound_url("http://127.0.0.1/admin")
    assert valid is False
    assert "Forbidden" in reason or "prohibited" in reason

    valid, reason = validate_outbound_url("http://localhost:8080/metrics")
    assert valid is False
    assert "Forbidden" in reason or "prohibited" in reason

def test_cloud_metadata_ip_blocked():
    # AWS, GCP, Azure, DigitalOcean link-local metadata address
    metadata_ip = "169.254.169.254"
    assert is_ip_allowed(metadata_ip) is False
    assert is_ip_allowed("169.254.1.1") is False

    valid, reason = validate_outbound_url(f"http://{metadata_ip}/latest/meta-data/")
    assert valid is False
    assert "prohibited" in reason or "Forbidden" in reason or "DNS" in reason

def test_private_rfc1918_networks_blocked():
    assert is_ip_allowed("10.0.0.1") is False
    assert is_ip_allowed("10.255.255.255") is False
    assert is_ip_allowed("172.16.0.1") is False
    assert is_ip_allowed("172.31.255.255") is False
    assert is_ip_allowed("192.168.1.1") is False
    assert is_ip_allowed("192.168.0.254") is False

    valid, reason = validate_outbound_url("http://10.0.0.1:8000/internal-api")
    assert valid is False

    valid, reason = validate_outbound_url("https://192.168.1.50/dashboard")
    assert valid is False

def test_unsupported_url_schemes_rejected():
    invalid_schemes = [
        "file:///etc/passwd",
        "ftp://mirror.internal/release",
        "gopher://ancient.service",
        "data:text/html,<script>alert(1)</script>",
        "javascript:alert(1)"
    ]
    for url in invalid_schemes:
        valid, reason = validate_outbound_url(url)
        assert valid is False
        assert "Prohibited URL scheme" in reason or "parse failure" in reason or "Missing hostname" in reason

def test_public_safe_destinations_allowed():
    # Standard public domain with valid DNS
    valid, res = validate_outbound_url("https://example.com")
    assert valid is True
    assert res != ""
