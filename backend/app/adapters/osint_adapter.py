"""
WebGuard Passive OSINT & Reconnaissance Adapter
Collects permitted public intelligence:
- DNS Records (A, AAAA, MX, NS, TXT, CAA, SPF, DMARC) via dnspython
- Domain Registration (RDAP - Registration Data Access Protocol)
- TLS Certificate Telemetry & Validity
"""

import time
import socket
import ssl
import datetime
from typing import Dict, Any, List, Optional
import httpx
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False

from .base import BaseEvidenceProvider, EvidenceResult, ProviderStatus
from ..utils.security import validate_outbound_url
from ..utils.domain_parser import normalize_domain, parse_registrable_domain

class OSINTAdapter(BaseEvidenceProvider):
    def __init__(self):
        super().__init__(name="passive_osint_provider", cache_ttl_seconds=3600)

    def query_dns_records(self, domain: str) -> Dict[str, Any]:
        """
        Queries permitted public DNS records (A, AAAA, MX, NS, TXT, CAA).
        Treats missing records as unknown / absent, not malicious.
        """
        norm_domain = normalize_domain(domain)
        dns_data: Dict[str, Any] = {
            "domain": norm_domain,
            "queried_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "records": {
                "A": [],
                "AAAA": [],
                "MX": [],
                "NS": [],
                "TXT": [],
                "CAA": [],
            },
            "spf_present": False,
            "dmarc_present": False,
            "caa_configured": False,
            "errors": []
        }

        if not DNS_AVAILABLE:
            dns_data["errors"].append("dnspython library unavailable; skipped advanced record enumeration.")
            # Fallback to basic socket lookup for A record
            try:
                ip = socket.gethostbyname(norm_domain)
                dns_data["records"]["A"].append(ip)
            except Exception as e:
                dns_data["errors"].append(f"Basic DNS lookup failed: {e}")
            return dns_data

        resolver = dns.resolver.Resolver()
        resolver.timeout = 3.0
        resolver.lifetime = 3.0

        # Query standard record types
        for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CAA"]:
            try:
                answers = resolver.resolve(norm_domain, rtype)
                for rdata in answers:
                    text_val = rdata.to_text().strip('"')
                    dns_data["records"][rtype].append(text_val)
                    if rtype == "TXT" and "v=spf1" in text_val.lower():
                        dns_data["spf_present"] = True
                    if rtype == "CAA":
                        dns_data["caa_configured"] = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
                continue
            except Exception as e:
                dns_data["errors"].append(f"{rtype} query error: {str(e)[:100]}")

        # Check DMARC at _dmarc.{domain}
        try:
            dmarc_answers = resolver.resolve(f"_dmarc.{norm_domain}", "TXT")
            for rdata in dmarc_answers:
                if "v=dmarc1" in rdata.to_text().lower():
                    dns_data["dmarc_present"] = True
        except Exception:
            dns_data["dmarc_present"] = False

        return dns_data

    def fetch_rdap_registration(self, domain: str) -> Dict[str, Any]:
        """
        Retrieves domain registration metadata via ICANN RDAP standard.
        Does not invent data; returns available: False if registry does not answer.
        """
        _, sld, tld = parse_registrable_domain(domain)
        reg_domain = f"{sld}.{tld}" if sld and tld else domain

        rdap_result: Dict[str, Any] = {
            "domain": reg_domain,
            "available": False,
            "registrar": "Unknown",
            "registration_date": None,
            "expiration_date": None,
            "last_updated": None,
            "nameservers": [],
            "status": [],
            "source": "ICANN RDAP Bootstrap",
            "retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # Validate outbound URL against SSRF
        target_url = f"https://rdap.org/domain/{reg_domain}"
        is_safe, _ = validate_outbound_url(target_url)
        if not is_safe:
            rdap_result["error"] = "Target URL rejected by outbound SSRF filter."
            return rdap_result

        try:
            with httpx.Client(timeout=4.0, follow_redirects=True) as client:
                resp = client.get(target_url, headers={"Accept": "application/rdap+json, application/json"})
                if resp.status_code == 200:
                    data = resp.json()
                    rdap_result["available"] = True
                    
                    # Extract events (registration, expiration, etc.)
                    for event in data.get("events", []):
                        action = event.get("eventAction")
                        date_str = event.get("eventDate")
                        if action in ("registration", "created"):
                            rdap_result["registration_date"] = date_str
                        elif action in ("expiration", "expiry"):
                            rdap_result["expiration_date"] = date_str
                        elif action in ("last changed", "last update"):
                            rdap_result["last_updated"] = date_str

                    # Extract entities / registrar
                    for entity in data.get("entities", []):
                        roles = entity.get("roles", [])
                        if "registrar" in roles:
                            vcard = entity.get("vcardArray", [])
                            if len(vcard) > 1 and isinstance(vcard[1], list):
                                for prop in vcard[1]:
                                    if len(prop) > 3 and prop[0] == "fn":
                                        rdap_result["registrar"] = prop[3]

                    # Extract nameservers
                    for ns in data.get("nameservers", []):
                        ns_name = ns.get("ldhName") or ns.get("handle")
                        if ns_name:
                            rdap_result["nameservers"].append(ns_name)

                    rdap_result["status"] = data.get("status", [])
                else:
                    rdap_result["error"] = f"RDAP provider returned status {resp.status_code}"
        except Exception as e:
            rdap_result["error"] = f"RDAP fetch timeout or network error: {str(e)[:120]}"

        return rdap_result

    def inspect_tls_certificate(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Inspects TLS certificate details, validity window, issuer, and SANs via safe socket.
        """
        norm_domain = normalize_domain(domain)
        cert_info: Dict[str, Any] = {
            "domain": norm_domain,
            "has_tls": False,
            "issuer": None,
            "subject": None,
            "valid_from": None,
            "valid_until": None,
            "days_remaining": None,
            "sans": [],
            "is_expired": False,
            "is_self_signed": False,
            "signature_algorithm": None,
            "error": None
        }

        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((norm_domain, port), timeout=3.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=norm_domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        cert_info["has_tls"] = True
                        
                        # Issuer & Subject
                        issuer_dict = dict(x[0] for x in cert.get("issuer", []))
                        subject_dict = dict(x[0] for x in cert.get("subject", []))
                        cert_info["issuer"] = issuer_dict.get("organizationName") or issuer_dict.get("commonName")
                        cert_info["subject"] = subject_dict.get("commonName")

                        # SANs
                        for san_type, san_val in cert.get("subjectAltName", []):
                            if san_type == "DNS":
                                cert_info["sans"].append(san_val)

                        # Validity dates
                        not_before_str = cert.get("notBefore")
                        not_after_str = cert.get("notAfter")
                        if not_before_str and not_after_str:
                            dt_format = "%b %d %H:%M:%S %Y %Z"
                            nb_dt = datetime.datetime.strptime(not_before_str, dt_format).replace(tzinfo=datetime.timezone.utc)
                            na_dt = datetime.datetime.strptime(not_after_str, dt_format).replace(tzinfo=datetime.timezone.utc)
                            now = datetime.datetime.now(datetime.timezone.utc)
                            
                            cert_info["valid_from"] = nb_dt.isoformat()
                            cert_info["valid_until"] = na_dt.isoformat()
                            remaining = (na_dt - now).days
                            cert_info["days_remaining"] = remaining
                            cert_info["is_expired"] = remaining < 0

                        # Check self-signed
                        if cert_info["issuer"] == cert_info["subject"] and cert_info["issuer"] is not None:
                            cert_info["is_self_signed"] = True
        except ssl.SSLCertVerificationError as e:
            cert_info["has_tls"] = True
            cert_info["error"] = f"Certificate verification failed: {e.verify_message}"
            if "self-signed" in str(e).lower():
                cert_info["is_self_signed"] = True
        except Exception as e:
            cert_info["error"] = f"TLS handshake failed: {str(e)[:120]}"

        return cert_info

    def collect_osint(self, domain: str) -> EvidenceResult:
        cache_key = f"osint:{domain}"
        cached = self.get_cached(cache_key)
        if cached:
            return cached

        dns_data = self.query_dns_records(domain)
        tls_data = self.inspect_tls_certificate(domain)
        rdap_data = self.fetch_rdap_registration(domain)

        data = {
            "dns": dns_data,
            "tls": tls_data,
            "rdap": rdap_data,
            "collected_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        res = EvidenceResult(
            provider_name=self.name,
            evidence_type="passive_osint",
            status=ProviderStatus.SUCCESS,
            confidence=0.95,
            data=data
        )
        self.set_cache(cache_key, res)
        return res

osint_adapter = OSINTAdapter()
