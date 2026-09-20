"""
Entropy & Secret Detection Engine
Calculates Shannon entropy and matches high-precision secret patterns.
"""
import math
import re
from typing import List, Tuple, Optional


def shannon_entropy(data: str) -> float:
    """Calculate the Shannon entropy of a string."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    char_counts = {}
    for char in data:
        char_counts[char] = char_counts.get(char, 0) + 1
    for count in char_counts.values():
        p_x = count / length
        entropy += - p_x * math.log2(p_x)
    return entropy


# Known high-confidence API token patterns
SECRET_PATTERNS = [
    ("AWS Access Key ID", re.compile(r"\b(AKIA[0-9A-Z]{16})\b"), 9.5),
    ("AWS Secret Key", re.compile(r"(?i)aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]"), 9.8),
    ("GitHub Personal Access Token", re.compile(r"\b(ghp_[A-Za-z0-9]{36}|github_pat_[A-Za-z0-9_]{82})\b"), 9.5),
    ("OpenAI API Key", re.compile(r"\b(sk-[A-Za-z0-9_-]{32,64})\b"), 9.0),
    ("Slack Token", re.compile(r"\b(xox[baprs]-[0-9A-Za-z]{10,48})\b"), 8.5),
    ("Stripe Secret Key", re.compile(r"\b(sk_live_[0-9a-zA-Z]{24})\b"), 9.0),
    ("Generic Private Key Header", re.compile(r"-----BEGIN (RSA|EC|OPENSSH|DSA|PGP) PRIVATE KEY-----"), 9.9),
    ("High-Entropy JWT Secret", re.compile(r"(?i)(jwt_secret|jwt_key|secret_key)\s*=\s*['\"]([^'\"]{10,})['\"]"), 8.8),
    ("Generic API Key Assignment", re.compile(r"(?i)(api_key|apikey|secret_token|auth_token)\s*=\s*['\"]([A-Za-z0-9_\-]{20,})['\"]"), 8.0),
]


def scan_line_for_secrets(line: str, min_entropy: float = 3.6) -> List[Tuple[str, str, float]]:
    """
    Scans a single line of text for exposed secrets.
    Returns: List of (SecretType, MatchedToken, CVSS_Score)
    """
    findings = []
    # Strip comments if needed, but often secrets are inside code assignments
    for label, pattern, score in SECRET_PATTERNS:
        match = pattern.search(line)
        if match:
            token = match.group(1) if match.groups() else match.group(0)
            # Filter obvious dummy/test strings
            if any(dummy in token.lower() for dummy in ["your_key", "xxx", "dummy", "placeholder", "example", "my_secret_here"]):
                continue
            # Check length and entropy if generic
            if "Generic" in label or "High-Entropy" in label:
                if len(token) >= 12 and shannon_entropy(token) >= min_entropy:
                    findings.append((label, token, score))
            else:
                findings.append((label, token, score))
    return findings
