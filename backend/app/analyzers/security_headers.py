"""
WebGuard Web Security Configuration & Security-Headers Analyzer
Evaluates HTTP response headers, cookie flags, TLS status, and redirect policy.
Produces structured findings aligned with NIST and OWASP guidance.
"""

import datetime
from typing import Dict, Any, List, Optional
from urllib.parse import urlparse
from ..models.security import SecurityFindingSchema

def evaluate_security_headers(
    url: str,
    headers: Dict[str, str],
    cookies: Optional[List[Dict[str, Any]]] = None,
    tls_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Evaluates response headers, cookies, and TLS state.
    Returns:
    - findings: List[SecurityFindingSchema]
    - header_scores: summary metrics
    - deductions: numerical risk score (0 to 100)
    """
    findings: List[SecurityFindingSchema] = []
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    parsed = urlparse(url)
    is_https = parsed.scheme == "https"

    # 1. Content-Security-Policy (CSP)
    csp = headers_lower.get("content-security-policy")
    if not csp:
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-CSP",
            category="headers",
            affected_url=url,
            severity="HIGH",
            confidence=1.0,
            message="Content-Security-Policy (CSP) header is missing.",
            evidence="Header 'Content-Security-Policy' was not returned by server.",
            security_impact="Increases vulnerability to Cross-Site Scripting (XSS), malicious script injection, and clickjacking.",
            remediation="Configure a restrictive Content-Security-Policy header defining trusted script-src, object-src, and default-src directives.",
            verification_status="verified"
        ))
    else:
        if "'unsafe-inline'" in csp.lower() and "nonce-" not in csp.lower():
            findings.append(SecurityFindingSchema(
                finding_id="SEC-HDR-CSP-UNSAFE-INLINE",
                category="headers",
                affected_url=url,
                severity="MEDIUM",
                confidence=0.95,
                message="Content-Security-Policy allows 'unsafe-inline' scripts without nonce protection.",
                evidence=f"CSP: {csp[:120]}...",
                security_impact="Allows inline JavaScript execution, significantly weakening XSS defense.",
                remediation="Replace 'unsafe-inline' with cryptographic script nonces or SHA-256 hashes.",
                verification_status="verified"
            ))

    # 2. Strict-Transport-Security (HSTS)
    hsts = headers_lower.get("strict-transport-security")
    if not is_https:
        findings.append(SecurityFindingSchema(
            finding_id="SEC-TLS-NO-HTTPS",
            category="tls",
            affected_url=url,
            severity="CRITICAL",
            confidence=1.0,
            message="Website serves unencrypted content over plain HTTP.",
            evidence=f"Protocol scheme is '{parsed.scheme}://'.",
            security_impact="Permits trivial eavesdropping, session hijacking, and man-in-the-middle content tampering.",
            remediation="Migrate entire site to HTTPS and configure permanent HTTP-to-HTTPS (301) redirects.",
            verification_status="verified"
        ))
    elif not hsts:
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-HSTS",
            category="headers",
            affected_url=url,
            severity="HIGH",
            confidence=1.0,
            message="HTTP Strict-Transport-Security (HSTS) header is missing.",
            evidence="Header 'Strict-Transport-Security' was not returned.",
            security_impact="Browsers may attempt initial connection over unencrypted HTTP, exposing users to SSL stripping attacks.",
            remediation="Add 'Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'.",
            verification_status="verified"
        ))
    else:
        # Check max-age duration
        if "max-age=" in hsts.lower():
            try:
                parts = hsts.lower().split("max-age=")[1].split(";")[0].strip()
                max_age_val = int(parts)
                if max_age_val < 10368000: # 120 days
                    findings.append(SecurityFindingSchema(
                        finding_id="SEC-HDR-HSTS-SHORT-MAXAGE",
                        category="headers",
                        affected_url=url,
                        severity="LOW",
                        confidence=1.0,
                        message="HSTS max-age duration is shorter than recommended 1 year baseline.",
                        evidence=f"Observed HSTS: {hsts}",
                        security_impact="Short expiration window leaves clients unprotected if visited infrequently.",
                        remediation="Set HSTS max-age to at least 31536000 seconds (1 year).",
                        verification_status="verified"
                    ))
            except Exception:
                pass

    # 3. X-Content-Type-Options
    xcto = headers_lower.get("x-content-type-options")
    if not xcto or xcto.lower().strip() != "nosniff":
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-XCTO",
            category="headers",
            affected_url=url,
            severity="MEDIUM",
            confidence=1.0,
            message="X-Content-Type-Options header is missing or not set to 'nosniff'.",
            evidence=f"Observed header: {xcto or 'None'}",
            security_impact="Browsers may MIME-sniff responses away from declared Content-Type, executing executable content in text/plain files.",
            remediation="Add 'X-Content-Type-Options: nosniff' to all HTTP responses.",
            verification_status="verified"
        ))

    # 4. X-Frame-Options (Clickjacking defense)
    xfo = headers_lower.get("x-frame-options")
    if not xfo and (not csp or "frame-ancestors" not in csp.lower()):
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-XFO",
            category="headers",
            affected_url=url,
            severity="MEDIUM",
            confidence=1.0,
            message="Anti-clickjacking protection missing (neither X-Frame-Options nor CSP frame-ancestors defined).",
            evidence="Headers 'X-Frame-Options' and 'frame-ancestors' are absent.",
            security_impact="Allows adversary websites to embed this application inside an invisible iframe to hijack user clicks.",
            remediation="Add 'X-Frame-Options: DENY' or configure 'frame-ancestors 'none'' in CSP.",
            verification_status="verified"
        ))

    # 5. Referrer-Policy
    ref_pol = headers_lower.get("referrer-policy")
    if not ref_pol:
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-REFERRER-POLICY",
            category="headers",
            affected_url=url,
            severity="LOW",
            confidence=1.0,
            message="Referrer-Policy header is missing.",
            evidence="Header 'Referrer-Policy' was not returned.",
            security_impact="Browsers may leak sensitive URL query parameters (tokens, session IDs) to third-party domains.",
            remediation="Set 'Referrer-Policy: strict-origin-when-cross-origin' or 'no-referrer'.",
            verification_status="verified"
        ))
    elif ref_pol.lower().strip() == "unsafe-url":
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-INSECURE-REFERRER",
            category="headers",
            affected_url=url,
            severity="MEDIUM",
            confidence=1.0,
            message="Referrer-Policy is set to insecure 'unsafe-url'.",
            evidence=f"Referrer-Policy: {ref_pol}",
            security_impact="Full URL with path and query parameters is disclosed on all outbound requests, including HTTP.",
            remediation="Change Referrer-Policy to 'strict-origin-when-cross-origin'.",
            verification_status="verified"
        ))

    # 6. Permissions-Policy
    perm_pol = headers_lower.get("permissions-policy")
    if not perm_pol:
        findings.append(SecurityFindingSchema(
            finding_id="SEC-HDR-NO-PERMISSIONS-POLICY",
            category="headers",
            affected_url=url,
            severity="LOW",
            confidence=1.0,
            message="Permissions-Policy header is missing.",
            evidence="Header 'Permissions-Policy' was not returned.",
            security_impact="Browser hardware APIs (camera, microphone, geolocation) are not explicitly restricted.",
            remediation="Add 'Permissions-Policy: geolocation=(), camera=(), microphone=()'.",
            verification_status="verified"
        ))

    # 7. Cookie Security Attribute Checks
    if cookies:
        for ck in cookies:
            ck_name = ck.get("name", "unknown")
            is_secure = ck.get("secure", False)
            is_httponly = ck.get("httpOnly", False)
            same_site = (ck.get("sameSite") or "").lower()

            if not is_secure and is_https:
                findings.append(SecurityFindingSchema(
                    finding_id="SEC-COOKIE-NO-SECURE",
                    category="cookies",
                    affected_url=url,
                    severity="HIGH",
                    confidence=1.0,
                    message=f"Cookie '{ck_name}' is missing the 'Secure' attribute.",
                    evidence=f"Cookie definition: {ck}",
                    security_impact="Cookie will be transmitted in unencrypted cleartext if client accesses any HTTP resource.",
                    remediation=f"Set the 'Secure' flag on cookie '{ck_name}'.",
                    verification_status="verified"
                ))

            if not is_httponly and any(token in ck_name.lower() for token in ["session", "auth", "token", "jwt", "id"]):
                findings.append(SecurityFindingSchema(
                    finding_id="SEC-COOKIE-NO-HTTPONLY",
                    category="cookies",
                    affected_url=url,
                    severity="HIGH",
                    confidence=1.0,
                    message=f"Session/auth cookie '{ck_name}' is missing the 'HttpOnly' flag.",
                    evidence=f"Cookie name: {ck_name}",
                    security_impact="Vulnerable to session theft via JavaScript `document.cookie` if an XSS flaw exists.",
                    remediation=f"Set 'HttpOnly' attribute on cookie '{ck_name}'.",
                    verification_status="verified"
                ))

            if same_site in ("", "none") and not is_secure:
                findings.append(SecurityFindingSchema(
                    finding_id="SEC-COOKIE-WEAK-SAMESITE",
                    category="cookies",
                    affected_url=url,
                    severity="MEDIUM",
                    confidence=1.0,
                    message=f"Cookie '{ck_name}' lacks restrictive SameSite attribute.",
                    evidence=f"SameSite value: {same_site or 'Unset'}",
                    security_impact="Increases susceptibility to Cross-Site Request Forgery (CSRF).",
                    remediation=f"Set 'SameSite=Lax' or 'SameSite=Strict' on cookie '{ck_name}'.",
                    verification_status="verified"
                ))

    # 8. TLS Certificate Telemetry Evaluation
    if tls_info:
        if tls_info.get("is_expired"):
            findings.append(SecurityFindingSchema(
                finding_id="SEC-TLS-EXPIRED-CERT",
                category="tls",
                affected_url=url,
                severity="CRITICAL",
                confidence=1.0,
                message="TLS certificate has expired.",
                evidence=f"Expired on: {tls_info.get('valid_until')}",
                security_impact="Browsers display prominent security warnings; prevents secure establishing of trust.",
                remediation="Renew TLS certificate immediately through your certificate authority.",
                verification_status="verified"
            ))
        elif tls_info.get("is_self_signed"):
            findings.append(SecurityFindingSchema(
                finding_id="SEC-TLS-SELF-SIGNED-CERT",
                category="tls",
                affected_url=url,
                severity="CRITICAL",
                confidence=1.0,
                message="TLS certificate is self-signed and not trusted by standard root CAs.",
                evidence=f"Issuer matches subject: '{tls_info.get('issuer')}'",
                security_impact="Leaves users vulnerable to man-in-the-middle attacks.",
                remediation="Install an SSL/TLS certificate issued by an authenticated public Certificate Authority.",
                verification_status="verified"
            ))
        elif tls_info.get("days_remaining") is not None and tls_info["days_remaining"] < 15:
            findings.append(SecurityFindingSchema(
                finding_id="SEC-TLS-CERT-EXPIRING-SOON",
                category="tls",
                affected_url=url,
                severity="MEDIUM",
                confidence=1.0,
                message=f"TLS certificate expires in {tls_info['days_remaining']} days.",
                evidence=f"Expiration date: {tls_info.get('valid_until')}",
                security_impact="Risk of unexpected production service disruption upon expiration.",
                remediation="Initiate automated certificate renewal via ACME / Let's Encrypt.",
                verification_status="verified"
            ))

    # Compute technical security score (0 = perfect, 100 = critical risk)
    severity_weights = {
        "CRITICAL": 35,
        "HIGH": 20,
        "MEDIUM": 10,
        "LOW": 4,
        "INFO": 0
    }
    raw_deductions = sum(severity_weights.get(f.severity, 0) for f in findings)
    technical_security_score = min(100, max(0, raw_deductions))

    # Level
    if technical_security_score >= 80:
        level = "CRITICAL_RISK"
    elif technical_security_score >= 50:
        level = "ELEVATED_RISK"
    elif technical_security_score >= 20:
        level = "ACCEPTABLE"
    else:
        level = "EXCELLENT"

    return {
        "score": technical_security_score,
        "level": level,
        "findings": findings,
        "findings_count": len(findings),
        "severity_breakdown": {
            "CRITICAL": sum(1 for f in findings if f.severity == "CRITICAL"),
            "HIGH": sum(1 for f in findings if f.severity == "HIGH"),
            "MEDIUM": sum(1 for f in findings if f.severity == "MEDIUM"),
            "LOW": sum(1 for f in findings if f.severity == "LOW"),
            "INFO": sum(1 for f in findings if f.severity == "INFO"),
        }
    }
