"""
Integration test suite for SentinelZero Core Scanner
"""
import os
from sentinelzero.core.scanner import SecurityScanner
from sentinelzero.reports.sarif import export_to_sarif
from sentinelzero.reports.json_exporter import export_to_json


def test_scan_vulnerable_repository():
    target = os.path.join(os.path.dirname(__file__), "fixtures", "vulnerable_repo")
    scanner = SecurityScanner(target)
    result = scanner.scan()

    assert result.scanned_files_count >= 2
    assert len(result.findings) >= 5
    assert result.posture.critical_count >= 2
    assert result.posture.score < 50
    assert "F" in result.posture.grade

    # Verify rule IDs detected
    detected_rules = {f.rule_id for f in result.findings}
    assert "SZ-001" in detected_rules  # Leaked OpenAI API key
    assert "SZ-003" in detected_rules  # Permissive CORS wildcard
    assert "SZ-004" in detected_rules  # Insecure JWT verify=False
    assert "SZ-005" in detected_rules  # Missing SSO guard
    assert "SZ-008" in detected_rules  # Pickle deserialization
    assert "SZ-009" in detected_rules  # Database password in URI
    assert "SZ-MCP-001" in detected_rules  # MCP Shell execution

    # Verify SARIF export works
    sarif = export_to_sarif(result)
    assert "SentinelZero" in sarif
    assert "SZ-001" in sarif

    # Verify JSON export works
    json_out = export_to_json(result)
    assert "posture" in json_out


def test_scan_secure_repository():
    target = os.path.join(os.path.dirname(__file__), "fixtures", "secure_repo")
    scanner = SecurityScanner(target)
    result = scanner.scan()

    assert result.scanned_files_count >= 1
    assert result.posture.critical_count == 0
    assert result.posture.high_count == 0
    assert result.posture.score >= 90
    assert "A" in result.posture.grade
