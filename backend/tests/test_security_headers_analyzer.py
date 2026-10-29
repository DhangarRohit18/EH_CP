"""
Automated Test Suite: Security Headers, TLS, and Cookie Policy Analyzer
Validates detection of missing headers (CSP, HSTS, XCTO, Referrer, Permissions, XFO),
insecure cookie attributes (missing Secure/HttpOnly), and TLS validity evaluation.
"""

import pytest
from app.analyzers.security_headers import evaluate_security_headers

def test_hardened_site_headers_returns_excellent_score():
    """
    A well-configured site with all defense-in-depth headers should receive a low risk score (EXCELLENT).
    """
    url = "https://secure-bank.example.com/login"
    headers = {
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'nonce-rAnd0m'; object-src 'none';",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
        "Server": "Cloudflare"
    }
    cookies = [
        {"name": "SESSIONID", "secure": True, "httpOnly": True, "sameSite": "Strict"}
    ]
    tls_info = {
        "has_tls": True,
        "is_expired": False,
        "is_self_signed": False,
        "days_remaining": 120
    }

    result = evaluate_security_headers(url, headers, cookies, tls_info)
    assert result["score"] < 20
    assert result["level"] == "EXCELLENT"
    assert result["severity_breakdown"]["CRITICAL"] == 0
    assert result["severity_breakdown"]["HIGH"] == 0

def test_missing_all_security_headers_flags_findings():
    """
    A site with zero security headers and plain HTTP should produce high/critical findings.
    """
    url = "http://insecure-shop.example.com"
    headers = {"Server": "Apache/2.4.41"}
    cookies = [
        {"name": "auth_token", "secure": False, "httpOnly": False, "sameSite": ""}
    ]

    result = evaluate_security_headers(url, headers, cookies, None)
    assert result["score"] >= 70
    assert result["level"] in ("ELEVATED_RISK", "CRITICAL_RISK")

    finding_ids = [f.finding_id for f in result["findings"]]
    assert "SEC-TLS-NO-HTTPS" in finding_ids
    assert "SEC-HDR-NO-CSP" in finding_ids
    assert "SEC-HDR-NO-XCTO" in finding_ids
    assert "SEC-COOKIE-NO-HTTPONLY" in finding_ids
    assert "SEC-COOKIE-WEAK-SAMESITE" in finding_ids

def test_expired_or_self_signed_tls_triggers_critical():
    url = "https://expired-cert.example.com"
    headers = {"Content-Security-Policy": "default-src 'self'"}
    tls_info = {
        "has_tls": True,
        "is_expired": True,
        "valid_until": "2023-01-01T00:00:00Z"
    }

    result = evaluate_security_headers(url, headers, [], tls_info)
    finding_ids = [f.finding_id for f in result["findings"]]
    assert "SEC-TLS-EXPIRED-CERT" in finding_ids
    assert any(f.severity == "CRITICAL" for f in result["findings"])
