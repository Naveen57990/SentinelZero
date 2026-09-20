"""
Automated Remediation & Zero-Trust Patch Generator
Generates unified diffs and applies automated security fixes to vulnerable source files.
"""
import difflib
import re
from typing import Optional
from .models import Vulnerability


def generate_patch_for_vulnerability(vuln: Vulnerability, original_file_content: str) -> Optional[str]:
    """
    Generates a unified diff patch string for a given vulnerability.
    """
    lines = original_file_content.splitlines(keepends=True)
    if vuln.line_number < 1 or vuln.line_number > len(lines):
        return None

    target_line = lines[vuln.line_number - 1]
    replacement_line = target_line

    if vuln.rule_id == "SZ-001":
        # Replace hardcoded secret with os.getenv
        # e.g. OPENAI_API_KEY = "sk-..." -> OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        m = re.search(r"([A-Za-z0-9_]+)\s*=\s*['\"][^'\"]+['\"]", target_line)
        if m:
            var_name = m.group(1)
            replacement_line = re.sub(
                r"=\s*['\"][^'\"]+['\"]",
                f"= os.getenv('{var_name}')",
                target_line
            )
            # Ensure import os exists if needed
            if "import os" not in original_file_content:
                lines.insert(0, "import os\n")

    elif vuln.rule_id == "SZ-003":
        # Replace allow_origins=["*"] with explicit domain
        replacement_line = re.sub(
            r"allow_origins\s*=\s*\[\s*['\"]\s*\*\s*['\"]\s*\]",
            "allow_origins=os.getenv('ALLOWED_ORIGINS', 'https://app.yourdomain.com').split(',')",
            target_line
        )

    elif vuln.rule_id == "SZ-004":
        # Remove verify=False from jwt decode
        replacement_line = re.sub(
            r",?\s*verify\s*=\s*False",
            ", verify=True",
            target_line
        )

    elif vuln.rule_id == "SZ-006":
        # Add httponly=True to set_cookie
        if "set_cookie" in target_line and "httponly" not in target_line:
            replacement_line = re.sub(
                r"\)$",
                ", httponly=True, secure=True, samesite='lax')",
                target_line.rstrip()
            ) + "\n"

    elif vuln.rule_id == "SZ-010":
        # Replace DEBUG = True with os.getenv
        replacement_line = re.sub(
            r"=\s*True",
            "= os.getenv('APP_DEBUG', 'False').lower() == 'true'",
            target_line
        )

    if replacement_line == target_line:
        return None

    new_lines = list(lines)
    # Adjust index if import os was inserted
    target_idx = vuln.line_number - 1 + (1 if "import os\n" in lines[:1] and "import os" not in original_file_content else 0)
    new_lines[target_idx] = replacement_line

    diff = difflib.unified_diff(
        lines,
        new_lines,
        fromfile=f"a/{vuln.file_path}",
        tofile=f"b/{vuln.file_path}",
        n=2
    )
    return "".join(diff)


def apply_patch_to_file(file_path: str, vuln: Vulnerability) -> bool:
    """
    Directly applies automated patch to target file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.splitlines(keepends=True)
        if vuln.line_number < 1 or vuln.line_number > len(lines):
            return False

        target_line = lines[vuln.line_number - 1]
        patch_applied = False

        if vuln.rule_id == "SZ-001":
            m = re.search(r"([A-Za-z0-9_]+)\s*=\s*['\"][^'\"]+['\"]", target_line)
            if m:
                var_name = m.group(1)
                lines[vuln.line_number - 1] = re.sub(
                    r"=\s*['\"][^'\"]+['\"]",
                    f"= os.getenv('{var_name}')",
                    target_line
                )
                if "import os" not in content:
                    lines.insert(0, "import os\n")
                patch_applied = True

        elif vuln.rule_id == "SZ-004":
            lines[vuln.line_number - 1] = re.sub(r",?\s*verify\s*=\s*False", ", verify=True", target_line)
            patch_applied = True

        elif vuln.rule_id == "SZ-010":
            lines[vuln.line_number - 1] = re.sub(r"=\s*True", "= os.getenv('APP_DEBUG', 'False').lower() == 'true'", target_line)
            patch_applied = True

        if patch_applied:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(lines)
            return True
        return False
    except Exception:
        return False
