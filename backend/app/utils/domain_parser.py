"""
WebGuard Domain Parser & Lookalike Detector
Handles registrable domain extraction, Unicode IDNA / Punycode normalization,
homograph attack identification, and Levenshtein typosquatting detection.
"""

import idna
from typing import Tuple, List, Optional
from ..engine.thresholds import BRAND_BENCHMARKS, SUSPICIOUS_TLDS

# Multi-part Public Suffixes commonly encountered
MULTI_PART_TLDS = {
    "co.uk", "org.uk", "me.uk", "ltd.uk", "plc.uk",
    "co.in", "net.in", "org.in", "gen.in", "firm.in", "ind.in",
    "com.au", "net.au", "org.au", "edu.au",
    "co.nz", "net.nz", "org.nz",
    "co.za", "org.za",
    "com.br", "org.br",
    "com.mx", "org.mx",
    "com.sg", "org.sg",
    "co.jp", "ne.jp", "or.jp",
    "com.cn", "net.cn", "org.cn"
}

def normalize_domain(domain_str: str) -> str:
    """
    Normalizes a domain string: strips protocol, path, port, converts to lowercase ASCII via IDNA.
    """
    clean = domain_str.strip().lower()
    if clean.startswith("http://"):
        clean = clean[7:]
    elif clean.startswith("https://"):
        clean = clean[8:]
    
    clean = clean.split("/")[0].split(":")[0]
    
    try:
        # Convert Unicode / Punycode
        clean = idna.decode(idna.encode(clean))
    except Exception:
        pass
    return clean

def parse_registrable_domain(domain: str) -> Tuple[str, str, str]:
    """
    Splits domain into (subdomain, sld, tld)
    e.g. 'checkout.deals.store.co.uk' -> ('checkout.deals', 'store', 'co.uk')
    """
    norm = normalize_domain(domain)
    parts = norm.split(".")
    if len(parts) <= 1:
        return ("", norm, "")

    # Check 2-part TLDs first
    if len(parts) >= 3:
        two_part_tld = f"{parts[-2]}.{parts[-1]}"
        if two_part_tld in MULTI_PART_TLDS:
            sld = parts[-3]
            sub = ".".join(parts[:-3])
            return (sub, sld, two_part_tld)

    # Standard 1-part TLD
    tld = parts[-1]
    sld = parts[-2]
    sub = ".".join(parts[:-2])
    return (sub, sld, tld)

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Computes Levenshtein edit distance between two strings.
    """
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

def detect_brand_mimicry(domain: str) -> Optional[dict]:
    """
    Inspects domain for typosquatting, brand mimicry, or misleading subdomains.
    Returns details if mimicry detected, None otherwise.
    """
    sub, sld, tld = parse_registrable_domain(domain)
    norm = normalize_domain(domain)

    # 1. Look for brand in subdomain spoofing (e.g. amazon.com.scam-site.org)
    for brand in BRAND_BENCHMARKS:
        if brand in sub and brand != sld:
            return {
                "type": "subdomain_spoofing",
                "brand": brand,
                "message": f"Brand '{brand}' appears inside subdomain of unrelated domain '{sld}.{tld}'.",
                "severity": "critical",
                "points": 45
            }

    # Normalize common l33tspeak substitutions (0->o, 1->l, 3->e, @->a, 5->s)
    de_leet_sld = (
        sld.replace("0", "o")
           .replace("1", "l")
           .replace("3", "e")
           .replace("@", "a")
           .replace("5", "s")
    )

    sld_tokens = sld.split("-")

    # 2. Look for Levenshtein typo distance on SLD (e.g. 'amazn', 'flipkrt', 'applle')
    # Filter out exact matches (the legitimate brand itself)
    for brand in BRAND_BENCHMARKS:
        if sld == brand:
            # Check if using suspicious high-abuse TLD
            if f".{tld}" in SUSPICIOUS_TLDS or tld not in ("com", "in", "org", "co.uk"):
                return {
                    "type": "brand_on_disposable_tld",
                    "brand": brand,
                    "message": f"Legitimate brand name '{brand}' operated under high-abuse TLD '.{tld}'.",
                    "severity": "critical",
                    "points": 50
                }
            return None # Legitimate brand SLD on standard TLD

        dist = levenshtein_distance(sld, brand)
        if 1 <= dist <= 2 and len(sld) >= 4 and abs(len(sld) - len(brand)) <= 2:
            return {
                "type": "typosquatting",
                "brand": brand,
                "distance": dist,
                "message": f"Possible typosquatting attack: '{sld}' is {dist} edit(s) away from trusted brand '{brand}'.",
                "severity": "critical",
                "points": 40
            }

        # Check hyphenated tokens (e.g. 'amaz0n' in 'amaz0n-prime-special')
        for token in sld_tokens:
            token_dist = levenshtein_distance(token, brand)
            if 1 <= token_dist <= 2 and len(token) >= 4 and abs(len(token) - len(brand)) <= 2:
                return {
                    "type": "typosquatting",
                    "brand": brand,
                    "distance": token_dist,
                    "message": f"Possible typosquatting attack: token '{token}' in '{sld}' mimics trusted brand '{brand}'.",
                    "severity": "critical",
                    "points": 45
                }

        # Substring mimicry: e.g. 'amazon-prime-deals' or 'amaz0n-prime-special'
        if (brand in sld or brand in de_leet_sld) and len(sld) > len(brand) + 2:
            return {
                "type": "brand_name_compound",
                "brand": brand,
                "message": f"Domain mimics brand name '{brand}' combined with commercial buzzwords in '{sld}'.",
                "severity": "high",
                "points": 40
            }

    return None
