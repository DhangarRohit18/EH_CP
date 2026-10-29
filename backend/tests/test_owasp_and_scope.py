"""
Automated Test Suite: OWASP Alignment & Scope Authorization
Validates mapping to OWASP Top 10 categories and strict backend scope enforcement.
"""

import pytest
from app.database import SessionLocal, Base, engine
from app.analyzers.owasp_passive import evaluate_owasp_alignment
from app.utils.scope_validator import is_domain_in_authorized_scope, register_scope_domain
from app.models.security import SecurityFindingSchema, TechItemSchema, CVEMatchSchema

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_owasp_top_10_mapping_and_version_disclosure():
    url = "https://example-shop.com"
    headers = {"Server": "Apache/2.4.41 (Ubuntu)", "Content-Type": "text/html"}
    findings = [
        SecurityFindingSchema(
            finding_id="SEC-TLS-WEAK",
            category="tls",
            affected_url=url,
            severity="HIGH",
            message="Weak TLS version"
        )
    ]
    technologies = [
        TechItemSchema(name="Apache", category="web_server", version="2.4.41", confidence=0.9, evidence="Server header")
    ]
    cve_matches = []

    res = evaluate_owasp_alignment(url, headers, findings, technologies, cve_matches, html_content="")
    categories = res["categories"]

    assert "A02_CryptographicFailures" in categories
    assert categories["A02_CryptographicFailures"]["status"] == "FAIL"

    assert "A05_SecurityMisconfiguration" in categories
    # Extra finding for version disclosure
    extra_ids = [f.finding_id for f in res["extra_findings"]]
    assert "OWASP-A05-VERSION-DISCLOSURE" in extra_ids

def test_scope_authorization_enforcement(db_session):
    test_domain = "authorized-target-lab.org"
    register_scope_domain(
        domain=test_domain,
        description="Authorized lab penetration test environment",
        authorized_by="security-lead@webguard.sec",
        db=db_session
    )

    # 1. Direct domain check
    is_auth, msg = is_domain_in_authorized_scope(test_domain, db_session)
    assert is_auth is True
    assert "Authorized under scope" in msg

    # 2. Subdomain check under authorized apex
    sub_domain = f"api.{test_domain}"
    is_auth_sub, msg_sub = is_domain_in_authorized_scope(sub_domain, db_session)
    assert is_auth_sub is True

    # 3. Unauthorized domain check
    is_auth_bad, msg_bad = is_domain_in_authorized_scope("malicious-unapproved-target.com", db_session)
    assert is_auth_bad is False
    assert "not registered" in msg_bad
