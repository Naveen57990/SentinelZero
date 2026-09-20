"""
SARIF Exporter
Converts SentinelZero findings into OASIS Standard SARIF 2.1.0 format.
"""
import json
from ..core.models import ScanResult, Severity


def export_to_sarif(scan_result: ScanResult) -> str:
    """Generates standard SARIF 2.1.0 JSON string."""
    sarif_rules = []
    seen_rules = set()
    results = []

    level_map = {
        Severity.CRITICAL: "error",
        Severity.HIGH: "error",
        Severity.MEDIUM: "warning",
        Severity.LOW: "note",
        Severity.INFO: "note",
    }

    for f in scan_result.findings:
        if f.rule_id not in seen_rules:
            seen_rules.add(f.rule_id)
            sarif_rules.append({
                "id": f.rule_id,
                "name": f.title,
                "shortDescription": {"text": f.title},
                "fullDescription": {"text": f.description},
                "help": {"text": f.remediation_advice},
                "properties": {
                    "cvss": f.cvss_score,
                    "category": f.category.value
                }
            })

        results.append({
            "ruleId": f.rule_id,
            "level": level_map.get(f.severity, "warning"),
            "message": {"text": f"{f.title}: {f.description}"},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": f.file_path},
                    "region": {
                        "startLine": f.line_number,
                        "snippet": {"text": f.snippet}
                    }
                }
            }]
        })

    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": "SentinelZero",
                    "version": scan_result.scanner_version,
                    "informationUri": "https://github.com/Naveen57990/SentinelZero",
                    "rules": sarif_rules
                }
            },
            "results": results
        }]
    }

    return json.dumps(sarif, indent=2)
