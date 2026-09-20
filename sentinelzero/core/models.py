"""
SentinelZero Data Models
Pydantic schemas for vulnerability findings, scan results, and security posture.
"""
from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Severity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class VulnerabilityCategory(str, Enum):
    CREDENTIAL_LEAK = "Credential & Secret Exposure"
    BROKEN_AUTHENTICATION = "Broken Authentication & SSO"
    EXCESSIVE_PERMISSIONS = "Excessive Permissions / MCP Risk"
    INJECTION = "Injection & Untrusted Input"
    SECURITY_MISCONFIGURATION = "Security Misconfiguration"
    INSECURE_COMMUNICATION = "Insecure Data & Cookie Exposure"


class Vulnerability(BaseModel):
    id: str
    rule_id: str
    title: str
    category: VulnerabilityCategory
    severity: Severity
    cvss_score: float = Field(..., ge=0.0, le=10.0)
    file_path: str
    line_number: int
    snippet: str
    description: str
    remediation_advice: str
    suggested_patch: Optional[str] = None


class SecurityPostureScore(BaseModel):
    score: int = Field(..., ge=0, le=100)
    grade: str
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    info_count: int
    total_findings: int


class ScanResult(BaseModel):
    scanner_version: str = "1.0.0"
    target_path: str
    timestamp: str
    scanned_files_count: int
    posture: SecurityPostureScore
    findings: List[Vulnerability]
    mcp_tool_findings: List[Vulnerability] = []
    metadata: Dict[str, Any] = {}
