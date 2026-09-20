"""
Model Context Protocol (MCP) & AI Agent Tool Security Auditor
Specialized analyzer for inspecting MCP manifests, tool schemas, and agent executor scripts.
"""
import json
import re
from typing import List, Dict, Any
from .models import Vulnerability, VulnerabilityCategory, Severity


def audit_mcp_tool_schema(schema_content: str, file_path: str) -> List[Vulnerability]:
    """
    Audits an MCP tool manifest (JSON or schema definition).
    Detects excessive blast radius, missing sanitization, and privileged capabilities.
    """
    findings = []
    
    # Try parsing as JSON first
    try:
        data = json.loads(schema_content)
        tools = []
        if isinstance(data, dict):
            if "tools" in data and isinstance(data["tools"], list):
                tools = data["tools"]
            elif "name" in data and ("inputSchema" in data or "description" in data):
                tools = [data]
        elif isinstance(data, list):
            tools = data

        for idx, tool in enumerate(tools):
            if not isinstance(tool, dict):
                continue
            name = tool.get("name", f"tool_{idx}")
            desc = (tool.get("description") or "").lower()
            input_schema = tool.get("inputSchema", {})
            properties = input_schema.get("properties", {}) if isinstance(input_schema, dict) else {}
            
            # Rule MCP-001: Arbitrary Shell / Command Execution
            if any(term in name.lower() or term in desc for term in ["bash", "shell", "exec_cmd", "run_terminal", "cli_command"]):
                findings.append(Vulnerability(
                    id=f"mcp-exec-{name}",
                    rule_id="SZ-MCP-001",
                    title=f"Unrestricted Shell Execution in MCP Tool '{name}'",
                    category=VulnerabilityCategory.EXCESSIVE_PERMISSIONS,
                    severity=Severity.CRITICAL,
                    cvss_score=9.6,
                    file_path=file_path,
                    line_number=1,
                    snippet=json.dumps(tool, indent=2)[:200],
                    description=f"Tool '{name}' permits arbitrary command/terminal execution. If invoked by an LLM via prompt injection, an attacker can compromise the host machine.",
                    remediation_advice="Restrict command execution to an explicit allowlist of non-destructive commands, enforce strict schema validation, or run in an isolated Docker sandbox."
                ))

            # Rule MCP-002: Path Traversal / Arbitrary File System Access
            if any(term in name.lower() or term in desc for term in ["read_file", "write_file", "delete_file", "file_system", "filesystem"]):
                if "path" in properties or "filepath" in properties or "filename" in properties:
                    path_prop = properties.get("path") or properties.get("filepath") or properties.get("filename") or {}
                    # Check if schema enforces pattern or restricted root directory
                    if not path_prop.get("pattern") and not "sandbox" in desc:
                        findings.append(Vulnerability(
                            id=f"mcp-pathtrav-{name}",
                            rule_id="SZ-MCP-002",
                            title=f"Unconfined File System Access in MCP Tool '{name}'",
                            category=VulnerabilityCategory.EXCESSIVE_PERMISSIONS,
                            severity=Severity.HIGH,
                            cvss_score=8.2,
                            file_path=file_path,
                            line_number=1,
                            snippet=json.dumps(tool, indent=2)[:200],
                            description=f"Tool '{name}' accepts file paths without root containment verification, exposing the host to directory traversal (e.g., accessing ../../etc/passwd or SSH keys).",
                            remediation_advice="Implement strict path normalization and chroot-like boundaries to confine all file operations to a dedicated workspace directory."
                        ))

            # Rule MCP-003: Missing Parameter Type Constraints / Wildcard Input
            if isinstance(input_schema, dict) and input_schema.get("type") == "object":
                for prop_name, prop_def in properties.items():
                    if isinstance(prop_def, dict) and not prop_def.get("type"):
                        findings.append(Vulnerability(
                            id=f"mcp-untyped-{name}-{prop_name}",
                            rule_id="SZ-MCP-003",
                            title=f"Untyped Wildcard Parameter in MCP Tool '{name}' ({prop_name})",
                            category=VulnerabilityCategory.SECURITY_MISCONFIGURATION,
                            severity=Severity.MEDIUM,
                            cvss_score=5.5,
                            file_path=file_path,
                            line_number=1,
                            snippet=f'"{prop_name}": {json.dumps(prop_def)}',
                            description=f"Parameter '{prop_name}' in tool '{name}' has no type constraint, allowing arbitrary payload injection to the backend handler.",
                            remediation_advice="Declare explicit schema types ('string', 'integer', 'boolean') and define regex patterns or enums."
                        ))
    except json.JSONDecodeError:
        # Fallback to structural regex analysis for Python/JS MCP server definitions
        pass

    # Static code pattern scanning for Python/JS MCP implementations
    lines = schema_content.splitlines()
    for idx, line in enumerate(lines, start=1):
        if re.search(r"@mcp\.tool|@server\.tool|server\.setRequestHandler", line):
            # Check following lines for subprocess or os.system calls
            window = "\n".join(lines[idx-1:min(len(lines), idx+25)])
            if re.search(r"subprocess\.(Popen|run|call)\([^)]*shell\s*=\s*True", window) or "os.system(" in window:
                findings.append(Vulnerability(
                    id=f"mcp-shell-true-{idx}",
                    rule_id="SZ-MCP-004",
                    title="MCP Tool Implementation Uses shell=True in Subprocess",
                    category=VulnerabilityCategory.INJECTION,
                    severity=Severity.CRITICAL,
                    cvss_score=9.8,
                    file_path=file_path,
                    line_number=idx,
                    snippet=line.strip(),
                    description="MCP tool handler invokes shell=True or os.system(). Untrusted inputs routed from model tool calls can trigger arbitrary remote code execution.",
                    remediation_advice="Use subprocess.run(['cmd', 'arg1'], shell=False) with strictly separated arguments and validate all model inputs."
                ))

    return findings
