"""
SentinelZero CLI Interface
High-impact terminal user interface powered by Rich.
"""
import sys
import os
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from .core.scanner import SecurityScanner
from .core.models import Severity
from .core.remediator import apply_patch_to_file
from .reports.sarif import export_to_sarif
from .reports.json_exporter import export_to_json

console = Console()


def print_banner():
    banner = Text(
        "⚡ SENTINELZERO :: Autonomous Zero-Trust API & MCP Security Auditor ⚡\n"
        "   Defending AI Agents, Cloud APIs & Zero-Trust Infrastructure",
        style="bold cyan"
    )
    console.print(Panel(banner, border_style="cyan", box=box.ROUNDED))


def main():
    parser = argparse.ArgumentParser(
        description="SentinelZero: Autonomous Zero-Trust API & MCP Security Auditor"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # scan command
    scan_parser = subparsers.add_parser("scan", help="Scan directory or file for security vulnerabilities")
    scan_parser.add_argument("target", nargs="?", default=".", help="Path to file or repository (default: .)")
    scan_parser.add_argument("--sarif", metavar="FILE", help="Export findings to SARIF file")
    scan_parser.add_argument("--json", metavar="FILE", help="Export findings to JSON file")
    scan_parser.add_argument("--fix", action="store_true", help="Automatically apply remediation patches")

    # audit-mcp command
    mcp_parser = subparsers.add_parser("audit-mcp", help="Audit Model Context Protocol (MCP) tool manifests")
    mcp_parser.add_argument("target", help="Path to MCP tool manifest JSON or directory")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        sys.exit(0)

    print_banner()

    if args.command in ["scan", "audit-mcp"]:
        target_path = getattr(args, "target", ".")
        console.print(f"[bold blue]🔍 Initiating Zero-Trust Audit on:[/bold blue] [bold white]{target_path}[/bold white]\n")

        scanner = SecurityScanner(target_path)
        result = scanner.scan()

        # Render Posture Score Card
        score = result.posture.score
        score_color = "green" if score >= 85 else "yellow" if score >= 60 else "red"
        
        posture_text = Text()
        posture_text.append(f"Security Posture Score: {score}/100\n", style=f"bold {score_color}")
        posture_text.append(f"Compliance Grade: {result.posture.grade}\n", style="bold white")
        posture_text.append(
            f"Findings Breakdown: {result.posture.critical_count} Critical | "
            f"{result.posture.high_count} High | {result.posture.medium_count} Medium | "
            f"{result.posture.low_count} Low\n",
            style="dim"
        )
        posture_text.append(f"Files Scanned: {result.scanned_files_count} | Scan Time: {result.metadata.get('scan_duration_ms', 0)}ms", style="dim cyan")

        console.print(Panel(posture_text, title="🛡️ Posture Evaluation", border_style=score_color, box=box.ROUNDED))

        # Render Table of Findings
        if result.findings:
            table = Table(title="🚨 Detected Security Vulnerabilities & Exposures", box=box.ROUNDED, header_style="bold magenta")
            table.add_column("Severity", style="bold", width=12)
            table.add_column("Rule ID", width=12)
            table.add_column("Title", width=36)
            table.add_column("Location", width=28)
            table.add_column("CVSS", justify="center", width=8)

            sev_colors = {
                Severity.CRITICAL: "bold red",
                Severity.HIGH: "bold orange3",
                Severity.MEDIUM: "bold yellow",
                Severity.LOW: "bold blue",
                Severity.INFO: "dim white"
            }

            for f in result.findings:
                table.add_row(
                    Text(f.severity.value, style=sev_colors.get(f.severity, "white")),
                    f.rule_id,
                    f.title,
                    f"{f.file_path}:{f.line_number}",
                    f"{f.cvss_score:.1f}"
                )

            console.print(table)
            console.print()

            # If fix flag provided, apply patches
            if getattr(args, "fix", False):
                console.print("[bold yellow]🛠️ Applying automated remediation patches...[/bold yellow]")
                fixed_count = 0
                for f in result.findings:
                    if f.suggested_patch:
                        full_file = os.path.join(result.target_path, f.file_path) if not os.path.isabs(f.file_path) else f.file_path
                        if apply_patch_to_file(full_file, f):
                            console.print(f"  [green]✓ Patched {f.rule_id} in {f.file_path}:{f.line_number}[/green]")
                            fixed_count += 1
                console.print(f"\n[bold green]✅ Applied {fixed_count} automated security remediations.[/bold green]\n")

        else:
            console.print("[bold green]✨ Clean Scan! Zero vulnerabilities or credential exposures detected.[/bold green]\n")

        # Handle SARIF Export
        if getattr(args, "sarif", None):
            sarif_content = export_to_sarif(result)
            with open(args.sarif, "w", encoding="utf-8") as f:
                f.write(sarif_content)
            console.print(f"[green]✓ SARIF report saved to: {args.sarif}[/green]")

        # Handle JSON Export
        if getattr(args, "json", None):
            json_content = export_to_json(result)
            with open(args.json, "w", encoding="utf-8") as f:
                f.write(json_content)
            console.print(f"[green]✓ JSON report saved to: {args.json}[/green]")

        # Exit code: 1 if critical/high vulnerabilities found, else 0
        if result.posture.critical_count > 0 or result.posture.high_count > 0:
            sys.exit(1)
        sys.exit(0)


if __name__ == "__main__":
    main()
