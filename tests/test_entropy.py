"""
Unit tests for Shannon entropy and secret detection
"""
from sentinelzero.core.entropy import shannon_entropy, scan_line_for_secrets


def test_shannon_entropy_calculation():
    # Low entropy repetitive string
    low_entropy = shannon_entropy("aaaaaaaaaaaaaaaa")
    assert low_entropy == 0.0

    # High entropy random token
    high_entropy = shannon_entropy("a8F9z!K2@mP0#qL9$vX1")
    assert high_entropy > 4.0


def test_secret_detection_patterns():
    # AWS Key (valid format without dummy keyword)
    aws_line = "AWS_KEY = 'AKIA1234567890ABCDEF'"
    findings = scan_line_for_secrets(aws_line)
    assert len(findings) == 1
    assert "AWS Access Key" in findings[0][0]

    # OpenAI Key
    openai_line = "client = OpenAI(api_key='sk-proj-999888777666555444333222111000')"
    findings = scan_line_for_secrets(openai_line)
    assert len(findings) >= 1
    assert "OpenAI API Key" in findings[0][0]

    # Clean Line (False Positive resistance)
    clean_line = "normal_variable = 'standard_string_without_secret'"
    findings = scan_line_for_secrets(clean_line)
    assert len(findings) == 0
