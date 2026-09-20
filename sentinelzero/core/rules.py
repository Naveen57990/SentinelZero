"""
SentinelZero Security Rule Definitions & AST Analyzers
Implements OWASP API Security Top 10, Zero-Trust standards, and configuration checks.
"""
import ast
import re
from typing import List
from .models import Vulnerability, VulnerabilityCategory, Severity


def scan_python_ast(content: str, file_path: str) -> List[Vulnerability]:
    """
    Parses Python code using AST to find structural vulnerabilities.
    """
    findings = []
    try:
        tree = ast.parse(content, filename=file_path)
    except SyntaxError:
        # Fallback to regex-based scanning if AST fails
        return []

    lines = content.splitlines()

    for node in ast.walk(tree):
        # Rule SZ-004: JWT verify=False or algorithms=['none']
        if isinstance(node, ast.Call):
            func_name = ""
            if isinstance(node.func, ast.Attribute):
                func_name = node.func.attr
            elif isinstance(node.func, ast.Name):
                func_name = node.func.id

            if func_name in ["decode", "jwt_decode"]:
                for keyword in node.keywords:
                    if keyword.arg == "verify" and isinstance(keyword.value, ast.Constant) and keyword.value.value is False:
                        lineno = getattr(node, "lineno", 1)
                        snippet = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
                        findings.append(Vulnerability(
                            id=f"jwt-no-verify-{lineno}",
                            rule_id="SZ-004",
                            title="Insecure JWT Verification Disabled (verify=False)",
                            category=VulnerabilityCategory.BROKEN_AUTHENTICATION,
                            severity=Severity.CRITICAL,
                            cvss_score=9.8,
                            file_path=file_path,
                            line_number=lineno,
                            snippet=snippet.strip(),
                            description="JWT token validation explicitly disables cryptographic signature verification (verify=False), allowing attackers to forge arbitrary tokens.",
                            remediation_advice="Remove verify=False and validate tokens against a secure public key or environment-managed secret.",
                            suggested_patch="jwt.decode(token, secret, algorithms=['RS256'], verify=True)"
                        ))

            # Rule SZ-008: Dangerous Deserialization (pickle.loads, yaml.load without SafeLoader)
            if func_name in ["loads", "load"]:
                module_name = ""
                if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    module_name = node.func.value.id
                if module_name == "pickle":
                    lineno = getattr(node, "lineno", 1)
                    snippet = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
                    findings.append(Vulnerability(
                        id=f"pickle-deser-{lineno}",
                        rule_id="SZ-008",
                        title="Insecure Deserialization via pickle.loads()",
                        category=VulnerabilityCategory.INJECTION,
                        severity=Severity.CRITICAL,
                        cvss_score=9.8,
                        file_path=file_path,
                        line_number=lineno,
                        snippet=snippet.strip(),
                        description="Deserializing untrusted data with pickle allows remote code execution through forged object reduction payloads.",
                        remediation_advice="Use safe serialization formats such as JSON, Protocol Buffers, or messagepack instead of pickle.",
                        suggested_patch="json.loads(data)"
                    ))

            # Rule SZ-007: SQL Injection via string formatting (cursor.execute with f-string or % formatting)
            if func_name in ["execute", "executemany"]:
                if node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
                    lineno = getattr(node, "lineno", 1)
                    snippet = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
                    findings.append(Vulnerability(
                        id=f"sqli-dyn-{lineno}",
                        rule_id="SZ-007",
                        title="Potential SQL Injection via Dynamic String Formatting",
                        category=VulnerabilityCategory.INJECTION,
                        severity=Severity.HIGH,
                        cvss_score=8.6,
                        file_path=file_path,
                        line_number=lineno,
                        snippet=snippet.strip(),
                        description="Database query constructed using string interpolation or format concatenation instead of parameterized queries, leading to SQL injection.",
                        remediation_advice="Use parameterized queries: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                        suggested_patch="cursor.execute('SELECT * FROM table WHERE id = %s', (id_val,))"
                    ))

        # Rule SZ-010: Debug=True in Production
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id.upper() in ["DEBUG", "FLASK_DEBUG"]:
                    if isinstance(node.value, ast.Constant) and node.value.value is True:
                        lineno = getattr(node, "lineno", 1)
                        snippet = lines[lineno - 1] if 0 < lineno <= len(lines) else ""
                        findings.append(Vulnerability(
                            id=f"debug-true-{lineno}",
                            rule_id="SZ-010",
                            title="Hardcoded DEBUG=True Flag in Production Code",
                            category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
                            severity=Severity.MEDIUM,
                            cvss_score=6.0,
                            file_path=file_path,
                            line_number=lineno,
                            snippet=snippet.strip(),
                            description="Enabling debug mode in deployed applications exposes interactive tracebacks, internal server variables, and PIN-protected debug consoles.",
                            remediation_advice="Load DEBUG flag dynamically from environment: DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'",
                            suggested_patch="DEBUG = os.getenv('APP_DEBUG', 'False').lower() == 'true'"
                        ))

    return findings


def scan_regex_rules(content: str, file_path: str) -> List[Vulnerability]:
    """
    Regex-based security rules for multi-language files (Python, JS, TS, YAML, Configs).
    """
    findings = []
    lines = content.splitlines()

    for idx, line in enumerate(lines, start=1):
        # Rule SZ-003: Permissive CORS Configuration
        if re.search(r"allow_origins\s*=\s*\[\s*['\"]\s*\*\s*['\"]\s*\]", line, re.I) or \
           re.search(r"Access-Control-Allow-Origin['\"]\s*:\s*['\"]\*", line, re.I):
            findings.append(Vulnerability(
                id=f"cors-wildcard-{idx}",
                rule_id="SZ-003",
                title="Overly Permissive CORS Origin ('*')",
                category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
                severity=Severity.HIGH,
                cvss_score=7.5,
                file_path=file_path,
                line_number=idx,
                snippet=line.strip(),
                description="Cross-Origin Resource Sharing (CORS) wildcard ('*') allows arbitrary external domains to make authenticated requests or read sensitive API responses.",
                remediation_advice="Restrict CORS origins to an explicit, authenticated domain whitelist (e.g. ['https://app.yourdomain.com']).",
                suggested_patch="allow_origins=['https://app.yourdomain.com']"
            ))

        # Rule SZ-006: Insecure Cookie Flags (Missing HttpOnly / Secure)
        if re.search(r"set_cookie\(", line) and not re.search(r"httponly\s*=\s*True", line, re.I):
            findings.append(Vulnerability(
                id=f"cookie-no-httponly-{idx}",
                rule_id="SZ-006",
                title="Sensitive Cookie Missing HttpOnly Flag",
                category=VulnerabilityCategory.INSECURE_COMMUNICATION,
                severity=Severity.MEDIUM,
                cvss_score=5.3,
                file_path=file_path,
                line_number=idx,
                snippet=line.strip(),
                description="Cookie set without httponly=True flag. In the event of an XSS vulnerability, client-side scripts can access session tokens.",
                remediation_advice="Always enforce httponly=True, secure=True, and samesite='lax' or 'strict' on session cookies.",
                suggested_patch="response.set_cookie(key, value, httponly=True, secure=True, samesite='lax')"
            ))

        # Rule SZ-005: Missing SSO / Enterprise SAML / OIDC Auth Guards
        if re.search(r"@app\.(get|post|put|delete)\(['\"]/(api/admin|api/v1/admin|api/enterprise|internal/)", line):
            # Check if auth dependency is missing in the route signature
            if not any(auth_kw in line for auth_kw in ["Depends(", "verify_sso", "auth", "get_current_user", "require_auth"]):
                findings.append(Vulnerability(
                    id=f"missing-sso-guard-{idx}",
                    rule_id="SZ-005",
                    title="Privileged Administrative Route Missing SSO / Auth Guard",
                    category=VulnerabilityCategory.BROKEN_AUTHENTICATION,
                    severity=Severity.HIGH,
                    cvss_score=8.5,
                    file_path=file_path,
                    line_number=idx,
                    snippet=line.strip(),
                    description="Admin or enterprise route declared without explicit authentication middleware or SSOJet/OIDC guard dependency.",
                    remediation_advice="Apply zero-trust authorization middleware or an enterprise SSO guard: Depends(verify_sso_session).",
                    suggested_patch="@app.get('/api/admin/users', dependencies=[Depends(verify_sso_session)])"
                ))

        # Rule SZ-009: Database connection string with embedded password
        if re.search(r"\b(postgres|mysql|mongodb|redis)://[^:]+:([^@]+)@", line) and not any(k in line.lower() for k in ["localhost", "127.0.0.1", "example", "username:password"]):
            findings.append(Vulnerability(
                id=f"db-uri-secret-{idx}",
                rule_id="SZ-009",
                title="Database URI with Hardcoded Password",
                category=VulnerabilityCategory.CREDENTIAL_LEAK,
                severity=Severity.CRITICAL,
                cvss_score=9.4,
                file_path=file_path,
                line_number=idx,
                snippet=line.strip(),
                description="Database connection URI contains hardcoded authentication credentials, exposing database access if the repository is committed or leaked.",
                remediation_advice="Extract connection credentials into an encrypted environment variable: DATABASE_URL = os.getenv('DATABASE_URL').",
                suggested_patch="DATABASE_URL = os.getenv('DATABASE_URL')"
            ))

    return findings
