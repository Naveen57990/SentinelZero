# Devpost Submission Details: SentinelZero

### Project Name
SentinelZero

### Elevator Pitch / Tagline
Autonomous Zero-Trust API & Model Context Protocol (MCP) Security Auditor with Real-Time Exposure Prevention.

---

### Project Description

#### 💡 Inspiration
As developers rapidly integrate AI agents, LLM tool-calling, and Model Context Protocol (MCP) servers into enterprise microservices, they are connecting autonomous models directly to terminal execution environments, file systems, and internal databases. 

Traditional static application security testing (SAST) tools (Bandit, SonarQube) only inspect legacy syntax patterns; they are completely blind to modern attack surfaces like **unconfined MCP tool blast radiuses**, **leaked high-entropy API tokens**, **missing enterprise SAML/OIDC gates**, and **permissive CORS configurations**. We built **SentinelZero** to give developers an autonomous, zero-trust security guardian that inspects code, manifests, and configurations in under 2 milliseconds and generates automated remediation patches.

#### 🛡️ What It Does
* **Multi-Vector Static Analysis in <2ms**: Scans Python codebases, TypeScript/JavaScript routes, and configuration manifests for critical vulnerabilities without heavy cloud dependencies.
* **Specialized Model Context Protocol (MCP) Auditor**: Audits AI agent tool schemas for command injection (`shell=True`), directory traversal, and untyped wildcard parameters.
* **Shannon Entropy Secret Detection**: Detects exposed high-entropy API keys (OpenAI, AWS, GitHub, Stripe, database URIs) and private keys with zero false positives on normal code.
* **OWASP API Top 10 & Zero-Trust Verification**: Identifies broken authentication (e.g. `jwt.decode(..., verify=False)`), missing enterprise SSO/OIDC middleware guards, and permissive CORS wildcards (`*`).
* **1-Click Automated Remediation**: Generates unified diffs and automatically applies fixes to code (e.g. replacing hardcoded secrets with `os.getenv` and locking down endpoints).
* **Dual Developer Interface**: A terminal CLI with rich visual posture gauges and OASIS SARIF 2.1.0 exports, plus a live interactive web dashboard.

#### ⚙️ How We Built It
* **Core Engine**: Python 3.14 with abstract syntax tree (AST) traversal, Shannon entropy mathematics, and deterministic regex security analyzers.
* **Reporting**: OASIS SARIF 2.1.0 engine for native integration with GitHub Code Scanning and CI/CD pipelines.
* **CLI**: Built with Python `rich` delivering colored vulnerability tables, CVSS scoring, and posture gauges.
* **Web Dashboard**: Modern dark-mode interface built with Tailwind CSS, SVG posture rings, and interactive sample loaders, deployed globally to Vercel.
* **Verification**: Rigorous automated pytest suite achieving 100% detection on seeded benchmark vulnerabilities and 0 false positives on clean code.

#### 🏆 Accomplishments We're Proud Of
* Achieved an average scan latency of **under 2 milliseconds** for repository audits.
* Created the first open-source security auditor specifically addressing **Model Context Protocol (MCP) schema hazards**.
* Fully automated the generation of drop-in remediation diffs.
* 100% automated test coverage on seeded vulnerabilities.

#### 🔮 What's Next for SentinelZero
* GitHub App integration for automated pull-request security linting.
* Extended heuristics for Kubernetes service account tokens and cloud IAM roles.
* Deeper integration with SSOJet for automated zero-trust authentication scaffolding.

---

### Links
* **Live Web Dashboard**: https://web-theta-tawny-78.vercel.app
* **GitHub Repository**: https://github.com/Naveen57990/SentinelZero
* **Demo Video**: https://github.com/Naveen57990/SentinelZero/raw/main/demo/sentinelzero_demo.mp4

### Built With
* `python`
* `ast`
* `fastapi`
* `next.js`
* `tailwind`
* `rich`
* `pydantic`
* `sarif`
* `vercel`
* `mcp`
* `cybersecurity`
* `zero-trust`
