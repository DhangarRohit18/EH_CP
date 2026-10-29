"""
Automated Test Suite: Developer Security & Static Code Analysis
Validates Bandit & Semgrep-aligned rule checking and non-executing static analysis.
"""

import os
import tempfile
import pytest
from app.utils.dev_security import scan_file_for_security_issues, run_repository_security_scan

def test_static_scanner_detects_eval_and_weak_hash():
    sample_code = """
import hashlib

def unsafe_calculation(user_input):
    # Intentional vulnerability for unit test verification
    result = eval(user_input)
    token = hashlib.md5(b"secret").hexdigest()
    return result, token
"""
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp:
        tmp.write(sample_code)
        tmp_path = tmp.name

    try:
        findings = scan_file_for_security_issues(tmp_path)
        rule_ids = [f["rule_id"] for f in findings]

        assert "BANDIT-B307-EVAL-USAGE" in rule_ids
        eval_finding = next(f for f in findings if f["rule_id"] == "BANDIT-B307-EVAL-USAGE")
        assert eval_finding["severity"] == "CRITICAL"
        assert "eval" in eval_finding["message"]

        assert "BANDIT-B303-WEAK-HASH" in rule_ids
        hash_finding = next(f for f in findings if f["rule_id"] == "BANDIT-B303-WEAK-HASH")
        assert hash_finding["severity"] == "HIGH"
    finally:
        os.remove(tmp_path)

def test_static_scanner_detects_jsx_dangerous_html():
    sample_jsx = """
import React from 'react';

export function UnsafeComponent({ htmlPayload }) {
    return <div dangerouslySetInnerHTML={{ __html: htmlPayload }} />;
}
"""
    with tempfile.NamedTemporaryFile("w", suffix=".tsx", delete=False) as tmp:
        tmp.write(sample_jsx)
        tmp_path = tmp.name

    try:
        findings = scan_file_for_security_issues(tmp_path)
        rule_ids = [f["rule_id"] for f in findings]
        assert "SEMGREP-JS-DANGEROUS-HTML" in rule_ids
    finally:
        os.remove(tmp_path)

def test_repository_scan_executes_safely():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scan_res = run_repository_security_scan(repo_root)

    assert scan_res["status"] == "completed"
    assert scan_res["scanned_files"] > 5
    assert "summary" in scan_res
    assert isinstance(scan_res["code_findings"], list)
