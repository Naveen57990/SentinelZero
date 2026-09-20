"""
JSON Exporter
Structured JSON output for SentinelZero dashboard integration.
"""
from ..core.models import ScanResult


def export_to_json(scan_result: ScanResult) -> str:
    return scan_result.model_dump_json(indent=2)
