"""
SentinelZero Core Scanner
Orchestrates file discovery, multi-vector rule execution, and posture score calculation.
"""
import os
import time
from typing import List, Set
from .models import (
    ScanResult,
    SecurityPostureScore,
    Vulnerability,
    VulnerabilityCategory,
    Severity
)
from .entropy import scan_line_for_secrets
from .rules import scan_python_ast, scan_regex_rules
from .mcp_auditor import audit_mcp_tool_schema
from .remediator import generate_patch_for_vulnerability

IGNORE_DIRS = {
    ".git", ".venv", "venv", "node_modules", "__pycache__",
    ".pytest_cache", "dist", "build", ".next", ".idea", ".vscode"
}

SUPPORTED_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".yaml", ".yml", ".env", ".env.example", ".toml"
}


class SecurityScanner:
    def __init__(self, target_path: str):
        self.target_path = os.path.abspath(target_path)
        self.scanned_files: Set[str] = set()
        self.findings: List[Vulnerability] = []
        self.mcp_findings: List[Vulnerability] = []

    def scan(self) -> ScanResult:
        """Executes full scan over target_path."""
        start_time = time.time()
        self.findings.clear()
        self.mcp_findings.clear()
        self.scanned_files.clear()

        if os.path.isfile(self.target_path):
            self._scan_file(self.target_path)
        elif os.path.isdir(self.target_path):
            for root, dirs, files in os.walk(self.target_path):
                # Prune ignored directories in-place
                dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext.lower() in SUPPORTED_EXTENSIONS or file.startswith(".env"):
                        full_path = os.path.join(root, file)
                        self._scan_file(full_path)

        posture = self._calculate_posture()

        return ScanResult(
            scanner_version="1.0.0",
            target_path=self.target_path,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            scanned_files_count=len(self.scanned_files),
            posture=posture,
            findings=self.findings,
            mcp_tool_findings=self.mcp_findings,
            metadata={"scan_duration_ms": round((time.time() - start_time) * 1000, 2)}
        )

    def _scan_file(self, file_path: str):
        """Scans an individual file."""
        self.scanned_files.add(file_path)
        rel_path = os.path.relpath(file_path, self.target_path)

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception:
            return

        lines = content.splitlines()

        # 1. Entropy & Secret Detection (line-by-line)
        for idx, line in enumerate(lines, start=1):
            secret_hits = scan_line_for_secrets(line)
            for label, token, score in secret_hits:
                vuln = Vulnerability(
                    id=f"secret-{idx}-{label[:6].lower()}",
                    rule_id="SZ-001",
                    title=f"Exposed Secret: {label}",
                    category=VulnerabilityCategory.CREDENTIAL_LEAK,
                    severity=Severity.CRITICAL if score >= 9.0 else Severity.HIGH,
                    cvss_score=score,
                    file_path=rel_path,
                    line_number=idx,
                    snippet=line.strip(),
                    description=f"High-entropy credential ({label}) hardcoded directly in source code. Exposed credentials can lead to full system/account takeover.",
                    remediation_advice="Revoke this credential immediately. Store secrets in environment variables (.env) or a secret manager (Vault / AWS Secrets Manager)."
                )
                vuln.suggested_patch = generate_patch_for_vulnerability(vuln, content)
                self.findings.append(vuln)

        # 2. Python AST Analysis
        if file_path.endswith(".py"):
            ast_hits = scan_python_ast(content, rel_path)
            for v in ast_hits:
                v.suggested_patch = generate_patch_for_vulnerability(v, content)
                self.findings.append(v)

        # 3. Multi-language Regex Rules
        regex_hits = scan_regex_rules(content, rel_path)
        for v in regex_hits:
            v.suggested_patch = generate_patch_for_vulnerability(v, content)
            self.findings.append(v)

        # 4. MCP Manifest & Agent Schema Auditor
        if "mcp" in file_path.lower() or "tool" in file_path.lower() or file_path.endswith(".json"):
            mcp_hits = audit_mcp_tool_schema(content, rel_path)
            for v in mcp_hits:
                self.mcp_findings.append(v)
                self.findings.append(v)

    def _calculate_posture(self) -> SecurityPostureScore:
        """Computes the zero-trust security score from 0 to 100."""
        crit = sum(1 for f in self.findings if f.severity == Severity.CRITICAL)
        high = sum(1 for f in self.findings if f.severity == Severity.HIGH)
        med = sum(1 for f in self.findings if f.severity == Severity.MEDIUM)
        low = sum(1 for f in self.findings if f.severity == Severity.LOW)
        info = sum(1 for f in self.findings if f.severity == Severity.INFO)
        total = len(self.findings)

        # Weighted penalty formula
        penalty = (crit * 25) + (high * 12) + (med * 5) + (low * 2)
        score = max(0, 100 - penalty)

        if score >= 90:
            grade = "A (Zero-Trust Compliant)"
        elif score >= 75:
            grade = "B (Acceptable - Moderate Risk)"
        elif score >= 60:
            grade = "C (Needs Hardening)"
        elif score >= 40:
            grade = "D (Critical Vulnerabilities Found)"
        else:
            grade = "F (Severe Exposure Risk)"

        return SecurityPostureScore(
            score=score,
            grade=grade,
            critical_count=crit,
            high_count=high,
            medium_count=med,
            low_count=low,
            info_count=info,
            total_findings=total
        )
