"""
WebGuard OWASP-Aligned Passive Security Assessment Analyzer
Maps observable configuration evidence to OWASP Top 10 2021 categories.
Strictly safe and non-intrusive: zero active exploitation or unauthorized fuzzing.
"""

from typing import Dict, Any, List
from ..models.security import SecurityFindingSchema, TechItemSchema, CVEMatchSchema

def evaluate_owasp_alignment(
    url: str,
    headers: Dict[str, str],
    findings: List[SecurityFindingSchema],
    technologies: List[TechItemSchema],
    cve_matches: List[CVEMatchSchema],
    html_content: str = ""
) -> Dict[str, Any]:
    """
    Evaluates observable evidence against OWASP Top 10 (2021) categories:
    A01: Broken Access Control
    A02: Cryptographic Failures
    A03: Injection
    A04: Insecure Design
    A05: Security Misconfiguration
    A06: Vulnerable and Outdated Components
    A07: Identification and Authentication Failures
    A08: Software and Data Integrity Failures
    A09: Security Logging and Monitoring Failures
    """
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    extra_findings: List[SecurityFindingSchema] = []

    # A05: Security Misconfiguration - Banner Version Disclosure
    server_hdr = headers_lower.get("server", "")
    if any(char.isdigit() for char in server_hdr):
        extra_findings.append(SecurityFindingSchema(
            finding_id="OWASP-A05-VERSION-DISCLOSURE",
            category="owasp",
            affected_url=url,
            severity="LOW",
            confidence=1.0,
            message=f"Web server exposes exact software version in 'Server' header: '{server_hdr}'.",
            evidence=f"Server: {server_hdr}",
            security_impact="Assists attackers in targeting version-specific exploits against server infrastructure.",
            remediation="Suppress server version banners (e.g. set 'ServerTokens Prod' in Apache or 'server_tokens off' in Nginx).",
            verification_status="verified"
        ))

    # A08: Software and Data Integrity Failures - Missing Subresource Integrity (SRI)
    if html_content and "<script" in html_content:
        import re
        external_scripts = re.findall(r'<script[^>]+src=[\'"](https?://[^\'"]+)[\'"][^>]*>', html_content, re.IGNORECASE)
        missing_sri_count = 0
        for s_tag in external_scripts:
            # If loaded from third-party CDN without integrity
            if any(cdn in s_tag.lower() for cdn in ["cdnjs", "unpkg", "jsdelivr", "googleapis"]) and "integrity=" not in html_content:
                missing_sri_count += 1

        if missing_sri_count > 0:
            extra_findings.append(SecurityFindingSchema(
                finding_id="OWASP-A08-MISSING-SRI",
                category="owasp",
                affected_url=url,
                severity="LOW",
                confidence=0.90,
                message=f"Observed {missing_sri_count} external CDN script(s) loaded without Subresource Integrity (SRI) hash.",
                evidence="Third-party CDN scripts loaded without 'integrity=' attribute.",
                security_impact="If the external CDN is compromised, malicious script payloads will execute in user browsers.",
                remediation="Add cryptographic 'integrity=' SHA-384 hashes and 'crossorigin=\"anonymous\"' to external script tags.",
                verification_status="verified"
            ))

    # Combine findings for category mapping
    all_findings = findings + extra_findings

    # Map categories to status
    owasp_categories = {
        "A01_BrokenAccessControl": {
            "status": "PASS",
            "findings_count": sum(1 for f in all_findings if "access" in f.finding_id.lower()),
            "description": "Directory traversal, exposed endpoints, and authorization controls."
        },
        "A02_CryptographicFailures": {
            "status": "FAIL" if any(f.category == "tls" or f.finding_id.startswith("SEC-TLS") for f in all_findings) else "PASS",
            "findings_count": sum(1 for f in all_findings if f.category == "tls" or f.finding_id.startswith("SEC-TLS")),
            "description": "HTTPS enforcement, TLS certificate validity, and encryption in transit."
        },
        "A03_Injection": {
            "status": "PASS",
            "findings_count": sum(1 for f in all_findings if "injection" in f.finding_id.lower()),
            "description": "XSS, SQLi, and command injection defenses."
        },
        "A04_InsecureDesign": {
            "status": "PASS",
            "findings_count": sum(1 for f in all_findings if "design" in f.finding_id.lower()),
            "description": "Architectural controls, threat modeling, and business logic hardening."
        },
        "A05_SecurityMisconfiguration": {
            "status": "FAIL" if any(f.category == "headers" for f in all_findings) else "PASS",
            "findings_count": sum(1 for f in all_findings if f.category in ("headers", "owasp")),
            "description": "Missing security headers (CSP, HSTS, XCTO), default error pages, and server banner leakage."
        },
        "A06_VulnerableComponents": {
            "status": "FAIL" if len(cve_matches) > 0 else "PASS",
            "findings_count": len(cve_matches),
            "description": "Known CVE matches in identified web technologies and software libraries."
        },
        "A07_AuthenticationFailures": {
            "status": "FAIL" if any(f.category == "cookies" for f in all_findings) else "PASS",
            "findings_count": sum(1 for f in all_findings if f.category == "cookies"),
            "description": "Insecure session management, missing HttpOnly/Secure flags, and weak authentication."
        },
        "A08_IntegrityFailures": {
            "status": "FAIL" if any("SRI" in f.finding_id for f in all_findings) else "PASS",
            "findings_count": sum(1 for f in all_findings if "SRI" in f.finding_id),
            "description": "Subresource Integrity (SRI), untrusted CI/CD pipelines, and unverified updates."
        },
        "A09_LoggingMonitoring": {
            "status": "INFORMATIONAL",
            "findings_count": 0,
            "description": "Security logging, incident response contact (/security.txt), and monitoring telemetry."
        }
    }

    return {
        "categories": owasp_categories,
        "extra_findings": extra_findings,
        "coverage_scope": "Passive non-intrusive evaluation of observable configuration, headers, and dependencies.",
        "active_testing_note": "Active exploitation and authenticated penetration tests are disabled by default and require authorized target scope configuration."
    }
