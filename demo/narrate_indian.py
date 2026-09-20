"""
Generates narration audio using macOS native Indian English voice 'Rishi'.
"""
import subprocess
import os

voice = "Rishi"
rate = 165

sections = [
    (
        "part_1_in.aiff",
        "As developers build autonomous AI agents and cloud APIs, they are silently introducing critical security vulnerabilities: exposed production keys, missing enterprise SSO gates, and Model Context Protocol tools with unconfined shell execution."
    ),
    (
        "part_2_in.aiff",
        "Meet SentinelZero. An autonomous, developer-first zero-trust security auditor. Engineered with deterministic AST parsing, Shannon entropy mathematics, and specialized MCP tool boundary inspection."
    ),
    (
        "part_3_in.aiff",
        "In a single command, SentinelZero audits your entire codebase in under two milliseconds. Here, it flags critical vulnerabilities: a leaked OpenAI key, an insecure JWT bypass, a database password, and an unrestricted terminal tool execution hazard, computing an urgent Posture Score of Grade F."
    ),
    (
        "part_4_in.aiff",
        "Now watch the live production dashboard in action. As we run the zero-trust audit, SentinelZero evaluates the live code, computes the visual posture ring, flags the unconfined MCP tools, and verifies compliance once remediated, bringing our security score back to Grade A."
    ),
    (
        "part_5_in.aiff",
        "Built for the TLN Cybersecurity Challenge 2026, SentinelZero is open-source, fully tested with six out of six passing test suites, and deployed live on Vercel. Try it today at our live dashboard."
    )
]

for filename, text in sections:
    out_path = os.path.join("demo", filename)
    cmd = ["say", "-v", voice, "-r", str(rate), text, "-o", out_path]
    subprocess.run(cmd, check=True)
    print(f"Rendered {filename} with voice {voice}")

