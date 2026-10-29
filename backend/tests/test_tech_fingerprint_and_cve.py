"""
Automated Test Suite: Technology Fingerprinting & CVE Correlation
Validates detection of web servers, runtimes, CMS, and framework signatures,
and authentic mapping to CVE identifiers with 'potentially_affected' status.
"""

import pytest
from app.analyzers.tech_fingerprint import fingerprint_technologies
from app.adapters.cve_adapter import cve_adapter
from app.models.security import TechItemSchema

def test_fingerprint_web_server_and_runtime_from_headers():
    headers = {
        "Server": "Apache/2.4.49 (Unix)",
        "X-Powered-By": "PHP/7.4.3"
    }
    technologies = fingerprint_technologies(headers)
    names = [t.name for t in technologies]
    assert "Apache" in names
    assert "PHP" in names

    apache_item = next(t for t in technologies if t.name == "Apache")
    assert apache_item.version == "2.4.49"
    assert apache_item.confidence >= 0.90

    php_item = next(t for t in technologies if t.name == "PHP")
    assert php_item.version == "7.4.3"

def test_fingerprint_cms_and_frontend_from_html():
    headers = {"Server": "cloudflare"}
    html_sample = """
    <html>
        <head>
            <meta name="generator" content="WordPress 5.8.1" />
            <script src="/static/js/react.production.min.js"></script>
        </head>
        <body>
            <div data-reactroot="">Content</div>
        </body>
    </html>
    """
    technologies = fingerprint_technologies(headers, html_content=html_sample)
    names = [t.name for t in technologies]
    assert "WordPress" in names
    assert "React" in names
    assert "Cloudflare" in names

    wp_item = next(t for t in technologies if t.name == "WordPress")
    assert wp_item.version == "5.8.1"

def test_cve_correlation_matches_vulnerable_apache():
    tech = [
        TechItemSchema(name="Apache", category="web_server", version="2.4.49", confidence=0.95, evidence="Server header")
    ]
    cves = cve_adapter.correlate_vulnerabilities(tech)
    cve_ids = [c.cve_id for c in cves]
    assert "CVE-2021-41773" in cve_ids
    
    match = next(c for c in cves if c.cve_id == "CVE-2021-41773")
    assert match.severity == "CRITICAL"
    assert match.cvss_score >= 9.0
    # Must distinguish potential vulnerability from confirmed exploitation
    assert match.verification_status == "potentially_affected"

def test_cve_correlation_unaffected_version_produces_no_false_positive():
    tech = [
        TechItemSchema(name="Apache", category="web_server", version="2.4.58", confidence=0.95, evidence="Server header")
    ]
    cves = cve_adapter.correlate_vulnerabilities(tech)
    assert len(cves) == 0, "Patched version should not match known 2.4.49/50 CVEs"
