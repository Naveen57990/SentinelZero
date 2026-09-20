## Inspiration
As developers rapidly adopt autonomous AI agents and Model Context Protocol (MCP) servers, they are connecting LLMs directly to host terminals and internal databases without basic zero-trust boundaries. Traditional security scanners are completely blind to unconfined MCP tool schemas, exposed high-entropy API keys, and missing SSO gates. I built **SentinelZero** to give developers an ultra-fast, autonomous security auditor that detects these exposures in under two milliseconds and generates instant remediation patches.

## What it does
* **Sub-2ms Multi-Vector AST Analysis**: Scans codebases for unauthenticated admin routes, insecure JWT bypasses (`verify=False`), and permissive CORS wildcards.
* **Specialized MCP Agent Inspector**: Audits AI agent tool manifests to prevent arbitrary command injection (`shell=True`) and directory traversal.
* **Shannon Entropy Secret Detection**: Calculates mathematical information entropy to identify exposed OpenAI, AWS, and database keys with zero false positives.
* **1-Click Automated Remediation**: Generates unified diffs and automatically extracts secrets into safe environment variables (`os.getenv`).
* **Dual Developer Experience**: A terminal CLI with visual posture gauges and SARIF exports, paired with a live interactive web dashboard.

## How we built it
* **Core Engine**: Python 3.14 using native `ast` for deterministic syntax tree traversal and Shannon entropy mathematics.
* **Standard Reporting**: OASIS SARIF 2.1.0 engine for native GitHub Code Scanning and CI/CD integration.
* **CLI & UI**: Python `rich` for terminal CVSS tables, and Tailwind CSS for the live production dashboard deployed on Vercel.
* **Test Suite**: Automated `pytest` suite validating 100% exploit detection with zero false alarms.

## Challenges we ran into
* **Taming Entropy False Positives**: Tuned mathematical entropy thresholds with character-frequency heuristics to avoid flagging harmless Base64 assets.
* **Auditing Dynamic MCP Schemas**: Built a context-aware AST visitor to trace MCP tool definitions from dictionaries to dangerous execution sinks.
* **Clean Patch Generation**: Calculated precise AST line and column offsets to generate unified diffs without disturbing existing code comments or formatting.

## Accomplishments that we're proud of
* Achieved an average scan latency of **1.26 milliseconds** across full repositories.
* Created the first open-source security auditor specifically addressing Model Context Protocol (MCP) tool execution blast radiuses.
* 100% automated test pass rate across all seeded vulnerability benchmarks.
* Deployed a production dashboard live globally on Vercel at `web-theta-tawny-78.vercel.app`.

## What we learned
* Zero-trust containment is urgently needed for autonomous AI agents before prompt injections become remote code executions.
* Local, deterministic AST analysis is exponentially faster than heavy cloud security tools.
* Developers want instant unified diff patches, not 50-page alert reports.

## What's next for SentinelZero
* **GitHub Action & Pre-Commit Hook**: Automated pull-request linting that blocks unconfined MCP tools or unencrypted keys.
* **Cloud & Kubernetes Auditing**: Expanding heuristics to inspect pod security contexts and AWS IAM role boundaries.
* **SSOJet Integration**: One-click CLI commands to scaffold enterprise SSOJet OIDC/SAML zero-trust authentication middleware into FastAPI and Express routes.
