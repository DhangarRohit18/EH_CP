"""
WebGuard Network Security & SSRF Protection Utility
Validates external URLs, verifies DNS resolution, and enforces safe network policies.
"""

import socket
import ipaddress
from urllib.parse import urlparse
from typing import Tuple

BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Private RFC1918
    ipaddress.ip_network("172.16.0.0/12"),     # Private RFC1918
    ipaddress.ip_network("192.168.0.0/16"),    # Private RFC1918
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / Cloud metadata (169.254.169.254)
    ipaddress.ip_network("0.0.0.0/8"),         # Broadcast / Current network
    ipaddress.ip_network("224.0.0.0/4"),       # Multicast
    ipaddress.ip_network("240.0.0.0/4"),       # Reserved
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 unique local
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
]

def is_ip_allowed(ip_str: str) -> bool:
    """
    Checks if an IP address is a safe, publicly routable destination.
    Returns False if private, loopback, link-local, multicast, or reserved.
    """
    try:
        ip = ipaddress.ip_address(ip_str)
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
    except ValueError:
        return False

def validate_outbound_url(url: str, allow_unresolvable: bool = False) -> Tuple[bool, str]:
    """
    Performs comprehensive SSRF checks on an outbound URL:
    - Verifies protocol is http or https
    - Resolves DNS hostname to IP addresses
    - Rejects any destination mapping to private, loopback, or metadata addresses
    Returns (is_valid, resolved_ip_or_error)
    """
    if not url:
        return False, "Empty URL"

    try:
        parsed = urlparse(url)
    except Exception as e:
        return False, f"URL parse failure: {e}"

    if parsed.scheme not in ("http", "https"):
        return False, f"Prohibited URL scheme: {parsed.scheme}"

    hostname = parsed.hostname
    if not hostname:
        return False, "Missing hostname in URL"

    # Reject direct internal hostnames
    low_host = hostname.lower()
    if low_host in ("localhost", "127.0.0.1", "0.0.0.0", "metadata.google.internal", "instance-data"):
        return False, f"Forbidden internal hostname: {hostname}"

    # Resolve hostname to IPv4/IPv6 addresses
    try:
        addr_info = socket.getaddrinfo(hostname, None)
    except socket.gaierror as e:
        if allow_unresolvable:
            return True, "unresolved"
        return False, f"DNS resolution failed for {hostname}: {e}"

    # Verify every resolved address
    for info in addr_info:
        sockaddr = info[4]
        ip_addr = sockaddr[0]
        if not is_ip_allowed(ip_addr):
            return False, f"Resolved IP {ip_addr} is in a prohibited private/internal network"

    return True, addr_info[0][4][0] if addr_info else ""
