"""
Unit tests for Model Context Protocol (MCP) tool security auditor
"""
from sentinelzero.core.mcp_auditor import audit_mcp_tool_schema
from sentinelzero.core.models import Severity


def test_mcp_unrestricted_shell_detection():
    manifest = """
    {
      "tools": [
        {
          "name": "run_bash_command",
          "description": "Execute terminal commands",
          "inputSchema": {"type": "object", "properties": {"cmd": {"type": "string"}}}
        }
      ]
    }
    """
    findings = audit_mcp_tool_schema(manifest, "mcp_test.json")
    assert len(findings) >= 1
    assert any(f.rule_id == "SZ-MCP-001" and f.severity == Severity.CRITICAL for f in findings)


def test_mcp_path_traversal_detection():
    manifest = """
    {
      "tools": [
        {
          "name": "read_file_data",
          "description": "Read contents of file",
          "inputSchema": {"type": "object", "properties": {"filepath": {}}}
        }
      ]
    }
    """
    findings = audit_mcp_tool_schema(manifest, "mcp_test.json")
    assert any(f.rule_id == "SZ-MCP-002" and f.severity == Severity.HIGH for f in findings)
