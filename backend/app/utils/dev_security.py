"""
WebGuard Developer Security & Static Code Analysis Utility
Scans source code files and dependency manifests for security vulnerabilities,
hardcoded secrets, weak cryptographic primitives, and injection patterns.
Strictly non-executing static analysis (Bandit & Semgrep aligned).
"""

import os
import re
import ast
import json
from typing import List, Dict, Any, Optional

DEV_SECURITY_RULES = [
    # Python Rules (Bandit / Semgrep aligned)
    {
        "id": "BANDIT-B307-EVAL-USAGE",
        "file_types": [".py"],
        "severity": "CRITICAL",
        "pattern": r"\b(?:eval|exec)\s*\(",
        "message": "Use of 'eval()' or 'exec()' detected.",
        "explanation": "Dynamic execution of arbitrary code allows arbitrary command execution if input is tainted.",
        "remediation": "Replace with safe alternatives like ast.literal_eval() or explicit parsers."
    },
    {
        "id": "BANDIT-B303-WEAK-HASH",
        "file_types": [".py"],
        "severity": "HIGH",
        "pattern": r"hashlib\.(?:md5|sha1)\s*\(",
        "message": "Cryptographically weak hash algorithm (MD5 or SHA1) detected.",
        "explanation": "MD5 and SHA1 suffer from practical collision attacks and are unsafe for cryptographic signatures.",
        "remediation": "Use SHA-256 (hashlib.sha256) or SHA-3 for hashing, or bcrypt/argon2 for password hashing."
    },
    {
        "id": "BANDIT-B105-HARDCODED-PASSWORD",
        "file_types": [".py", ".ts", ".js"],
        "severity": "HIGH",
        "pattern": r"(?:password|secret|api_key|token)\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]",
        "message": "Possible hardcoded credential or API secret string literal detected.",
        "explanation": "Embedding credentials in source code exposes secrets via repository version control.",
        "remediation": "Load credentials from environment variables or a secure key management system."
    },
    {
        "id": "BANDIT-B608-SQL-FORMAT-STRING",
        "file_types": [".py"],
        "severity": "HIGH",
        "pattern": r"(?:execute|raw)\s*\(\s*f['\"].*SELECT.*['\"]",
        "message": "Possible SQL injection: Python f-string used in database execution.",
        "explanation": "Constructing SQL queries using string formatting permits SQL injection attacks.",
        "remediation": "Use parameterized queries or SQLAlchemy ORM query methods."
    },
    {
        "id": "SEMGREP-JS-DANGEROUS-HTML",
        "file_types": [".ts", ".tsx", ".js"],
        "severity": "HIGH",
        "pattern": r"dangerouslySetInnerHTML\s*=",
        "message": "Use of 'dangerouslySetInnerHTML' detected in frontend code.",
        "explanation": "Direct insertion of untrusted raw HTML exposes the application to Cross-Site Scripting (XSS).",
        "remediation": "Use standard React JSX text bindings or sanitize with DOMPurify."
    },
    {
        "id": "SEMGREP-PYTHON-INSECURE-BINDING",
        "file_types": [".py"],
        "severity": "MEDIUM",
        "pattern": r"host\s*=\s*['\"]0\.0\.0\.0['\"]\s*,\s*port\s*=\s*[0-9]+(?!\s*,\s*ssl_context)",
        "message": "Service bound to all network interfaces (0.0.0.0) without explicit TLS in dev config.",
        "explanation": "Binding to 0.0.0.0 exposes internal endpoints to the local network.",
        "remediation": "Bind to 127.0.0.1 for local services, or enforce reverse-proxy authentication."
    }
]

def scan_file_for_security_issues(file_path: str) -> List[Dict[str, Any]]:
    """
    Safely scans an individual source file against static security rules.
    """
    findings: List[Dict[str, Any]] = []
    if not os.path.exists(file_path):
        return findings

    _, ext = os.path.splitext(file_path)

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            for rule in DEV_SECURITY_RULES:
                if ext in rule["file_types"]:
                    if re.search(rule["pattern"], line, re.IGNORECASE):
                        # Filter out test assertions or comment matches
                        if "#" in line and line.strip().startswith("#"):
                            continue
                        if "//" in line and line.strip().startswith("//"):
                            continue

                        findings.append({
                            "rule_id": rule["id"],
                            "file_path": os.path.relpath(file_path),
                            "line_number": line_num,
                            "severity": rule["severity"],
                            "snippet": line.strip()[:100],
                            "message": rule["message"],
                            "explanation": rule["explanation"],
                            "remediation": rule["remediation"]
                        })
    except Exception as e:
        pass

    return findings

def audit_dependencies(root_dir: str) -> List[Dict[str, Any]]:
    """
    Inspects package manifests for known insecure dependency versions.
    """
    dep_findings: List[Dict[str, Any]] = []
    
    # Audit Python requirements.txt
    req_path = os.path.join(root_dir, "backend", "requirements.txt")
    if os.path.exists(req_path):
        try:
            with open(req_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Check for outdated urllib3 or requests known CVEs
                if "urllib3<1.26.17" in content:
                    dep_findings.append({
                        "package": "urllib3",
                        "severity": "HIGH",
                        "advisory": "CVE-2023-43804: Cookie leakage on cross-origin redirects.",
                        "remediation": "Upgrade urllib3 to >= 1.26.17 or >= 2.0.6"
                    })
        except Exception:
            pass

    return dep_findings

def run_repository_security_scan(target_dir: str) -> Dict[str, Any]:
    """
    Executes a complete static analysis scan over repository codebase.
    """
    all_findings: List[Dict[str, Any]] = []
    scanned_files_count = 0

    ignored_dirs = {"node_modules", "dist", ".git", ".pytest_cache", "venv", ".venv", "__pycache__"}

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        for file in files:
            if file.endswith((".py", ".ts", ".tsx", ".js")):
                full_path = os.path.join(root, file)
                # Don't scan tests for fake test secrets
                if "tests" in full_path:
                    continue
                file_findings = scan_file_for_security_issues(full_path)
                all_findings.extend(file_findings)
                scanned_files_count += 1

    dep_findings = audit_dependencies(target_dir)

    return {
        "status": "completed",
        "scanned_files": scanned_files_count,
        "findings_count": len(all_findings),
        "code_findings": all_findings,
        "dependency_findings": dep_findings,
        "summary": {
            "CRITICAL": sum(1 for f in all_findings if f["severity"] == "CRITICAL"),
            "HIGH": sum(1 for f in all_findings if f["severity"] == "HIGH"),
            "MEDIUM": sum(1 for f in all_findings if f["severity"] == "MEDIUM"),
            "LOW": sum(1 for f in all_findings if f["severity"] == "LOW"),
        }
    }
