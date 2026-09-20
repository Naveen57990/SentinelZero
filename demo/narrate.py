import subprocess
import os

sections = [
    # (filename, text, target_voice, rate)
    (
        "part_1.aiff",
        "As developers build autonomous AI agents and cloud APIs, they are silently introducing critical security risks: exposed production API keys, missing enterprise SSO gates, and Model Context Protocol tools with unconfined shell execution.",
        "Daniel",
        180
    ),
    (
        "part_2.aiff",
        "Meet SentinelZero. An autonomous, developer-first zero-trust security auditor. Engineered with deterministic AST parsing, Shannon entropy mathematics, and specialized MCP tool boundary inspection.",
        "Daniel",
        180
    ),
    (
        "part_3.aiff",
        "In a single command, SentinelZero audits your entire codebase in under two milliseconds. Here, it flags critical vulnerabilities: a leaked OpenAI key, an insecure JWT bypass, a database password, and an unrestricted terminal tool execution hazard, computing an urgent Posture Score of Grade F.",
        "Daniel",
        180
    ),
    (
        "part_4.aiff",
        "With the fix flag, SentinelZero generates instant unified diffs, extracting credentials into secure environment variables and restoring the zero-trust posture score back to Grade A. Developers can inspect these findings visually on our deployed live dashboard.",
        "Daniel",
        180
    ),
    (
        "part_5.aiff",
        "Built for the TLN Cybersecurity Challenge 2026, SentinelZero is open-source, fully tested, and ready to protect the next generation of AI agent infrastructure. Try it live today at our Vercel dashboard.",
        "Daniel",
        180
    )
]

for filename, text, voice, rate in sections:
    out_path = os.path.join("demo", filename)
    cmd = ["say", "-v", voice, "-r", str(rate), text, "-o", out_path]
    subprocess.run(cmd, check=True)
    print(f"Rendered {filename}")

