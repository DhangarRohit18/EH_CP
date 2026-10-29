"""
WebGuard Technology Fingerprinting Analyzer
Identifies web servers, CMS platforms, frontend/backend frameworks, and runtime versions
using public HTTP headers, HTML metadata, script sources, and cookie indicators.
"""

import re
from typing import Dict, Any, List, Optional
from ..models.security import TechItemSchema

TECH_SIGNATURES = [
    # Web Servers
    {"name": "Nginx", "category": "web_server", "header": "server", "pattern": r"nginx(?:/([0-9.]+))?"},
    {"name": "Apache", "category": "web_server", "header": "server", "pattern": r"apache(?:/([0-9.]+))?"},
    {"name": "Cloudflare", "category": "cdn", "header": "server", "pattern": r"cloudflare"},
    {"name": "LiteSpeed", "category": "web_server", "header": "server", "pattern": r"litespeed"},
    {"name": "Microsoft-IIS", "category": "web_server", "header": "server", "pattern": r"microsoft-iis(?:/([0-9.]+))?"},
    {"name": "Caddy", "category": "web_server", "header": "server", "pattern": r"caddy(?:/([0-9.]+))?"},

    # Backend Runtimes & Languages
    {"name": "PHP", "category": "runtime", "header": "x-powered-by", "pattern": r"php(?:/([0-9.]+))?"},
    {"name": "ASP.NET", "category": "framework", "header": "x-powered-by", "pattern": r"asp\.net"},
    {"name": "Express", "category": "framework", "header": "x-powered-by", "pattern": r"express"},

    # CMS Platforms (via generator tag or headers)
    {"name": "WordPress", "category": "cms", "meta_generator": r"wordpress\s*([0-9.]+)?", "html_pattern": r"/wp-content/|/wp-includes/"},
    {"name": "Shopify", "category": "cms", "header": "x-shopify-stage", "pattern": r".*", "html_pattern": r"cdn\.shopify\.com"},
    {"name": "Magento", "category": "cms", "cookie": "frontend", "html_pattern": r"mage/cookies\.js|static/frontend/"},
    {"name": "WooCommerce", "category": "cms", "meta_generator": r"woocommerce\s*([0-9.]+)?", "html_pattern": r"woocommerce"},
    {"name": "Drupal", "category": "cms", "header": "x-generator", "pattern": r"drupal\s*([0-9.]+)?", "meta_generator": r"drupal\s*([0-9.]+)"},

    # Frontend Frameworks (via script tags or HTML attributes)
    {"name": "React", "category": "framework", "html_pattern": r"react\.production\.min\.js|data-reactroot|_reactRootContainer|react-dom"},
    {"name": "Vue.js", "category": "framework", "html_pattern": r"vue\.runtime\.min\.js|data-v-[a-f0-9]+|vue\.min\.js"},
    {"name": "Next.js", "category": "framework", "html_pattern": r"/_next/static/|__NEXT_DATA__"},
    {"name": "Angular", "category": "framework", "html_pattern": r"ng-version=\"([0-9.]+)\"|angular\.min\.js"},
    {"name": "jQuery", "category": "framework", "html_pattern": r"jquery[.-]([0-9.]+)(?:\.min)?\.js"}
]

def fingerprint_technologies(
    headers: Dict[str, str],
    html_content: Optional[str] = None,
    cookies: Optional[List[Dict[str, Any]]] = None
) -> List[TechItemSchema]:
    """
    Detects active technologies with confidence scores and evidence strings.
    """
    detected: List[TechItemSchema] = []
    seen_names = set()
    headers_lower = {k.lower(): v for k, v in (headers or {}).items()}
    html_str = html_content or ""
    cookie_names = [c.get("name", "") for c in (cookies or [])]

    for sig in TECH_SIGNATURES:
        name = sig["name"]
        cat = sig["category"]
        version = None
        evidence = None
        confidence = 0.0

        # 1. Header match
        if "header" in sig:
            hdr_val = headers_lower.get(sig["header"])
            if hdr_val:
                match = re.search(sig["pattern"], hdr_val, re.IGNORECASE)
                if match:
                    confidence = 0.95
                    evidence = f"HTTP Header '{sig['header']}: {hdr_val}'"
                    if match.groups() and match.group(1):
                        version = match.group(1)

        # 2. Meta generator tag
        if not evidence and "meta_generator" in sig and html_str:
            meta_match = re.search(rf"<meta[^>]*name=[\"']generator[\"'][^>]*content=[\"']([^\"']*{sig['meta_generator']}[^\"']*)[\"']", html_str, re.IGNORECASE)
            if meta_match:
                confidence = 0.90
                evidence = f"HTML Meta tag: {meta_match.group(0)[:80]}"
                ver_match = re.search(sig["meta_generator"], meta_match.group(1), re.IGNORECASE)
                if ver_match and ver_match.groups() and ver_match.group(1):
                    version = ver_match.group(1)

        # 3. HTML / Script pattern
        if not evidence and "html_pattern" in sig and html_str:
            html_match = re.search(sig["html_pattern"], html_str, re.IGNORECASE)
            if html_match:
                confidence = 0.80
                evidence = f"DOM/Script asset pattern match: '{html_match.group(0)}'"
                if html_match.groups() and html_match.group(1):
                    version = html_match.group(1)

        # 4. Cookie indicator
        if not evidence and "cookie" in sig:
            if sig["cookie"] in cookie_names:
                confidence = 0.75
                evidence = f"Session cookie '{sig['cookie']}'"

        if evidence and name not in seen_names:
            seen_names.add(name)
            detected.append(TechItemSchema(
                name=name,
                category=cat,
                version=version,
                confidence=confidence,
                evidence=evidence
            ))

    return detected
