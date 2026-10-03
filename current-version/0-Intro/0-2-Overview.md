# Overview

## From DevOps to DevSecOps

DevOps unified development and operations to deliver software faster and more reliably through automation, continuous integration, and continuous delivery. **DevSecOps** extends that model by making security a shared responsibility integrated into every phase, rather than a separate audit performed at the end.

The driving idea is **shift-left**: move security feedback as close as possible to the moment code is written, when issues are cheapest to fix. In practice, mature programs now **shift everywhere** — running fast, low-friction checks early *and* deeper validation continuously through build, test, deploy, and runtime.

The difference is not just where security happens, but *who owns it*: DevSecOps moves security ownership from a separate team to the whole engineering organization, supported by automation, tooling, and a champions network.

## What to add to a pipeline

A reasonable progression of controls to introduce:

- **Secrets scanning** — find credentials before they are committed or merged. Tools like TruffleHog and Gitleaks run in pre-commit hooks or CI with near-zero false-positive rates on high-entropy strings and known secret formats. A single leaked cloud credential can compromise an entire environment within minutes of appearing in a public repo.
- **SCA (Software Composition Analysis)** — detect vulnerable and malicious open-source dependencies. SCA tools map your dependency tree against CVE databases and increasingly flag malicious packages (typosquatting, dependency confusion) and license issues. Log4Shell (2021) demonstrated what a critical CVE in a transitive dependency can do at scale: hundreds of millions of systems affected by a library most of their developers had never heard of.
- **SAST (Static Application Security Testing)** — analyze first-party source code for flaws. Effective SAST runs in the pull request and reports only *new* findings against the base branch so developers see only what they introduced.
- **IaC scanning** — find misconfigurations in Terraform, Helm, Kubernetes manifests, Ansible, etc. These flaws — overly permissive IAM, unencrypted storage, open network rules — are frequently the easiest path into cloud environments. The Capital One breach (2019) exploited a misconfigured WAF combined with excessive IAM permissions to exfiltrate over 100 million records.
- **Container security** — scan and harden images and their base layers. Container scanning should run at build time and again continuously against the registry, since new CVEs emerge after an image is published.
- **Supply-chain security** — generate SBOMs, sign artifacts, and produce build provenance (SLSA). Signed provenance lets you verify that a release artifact was built from the expected source by the expected pipeline, catching tampering before production. The SolarWinds attack (2020) injected malicious code into the build process; signed provenance would have created a verifiable record of the anomaly.
- **IAST / DAST** — test running applications interactively and dynamically. IAST instruments the application at test time for deep, low-noise findings; DAST probes from the outside, as an attacker would.
- **API security** — discover, test, and protect APIs. REST and GraphQL surfaces are often undertested; dedicated API security tools enumerate endpoints from specs, traffic, or code and fuzz them for the OWASP API Top 10.
- **CNAPP / cloud-native security** — protect cloud and Kubernetes workloads at runtime. CNAPP platforms (CSPM + CWPP + CIEM + KSPM) give a unified view of misconfigurations, vulnerable workloads, excessive permissions, and runtime threats.
- **Continuous monitoring and vulnerability management** — aggregate, prioritize, and remediate findings over time. A vulnerability management process with defined SLAs (e.g., critical CVEs within 7 days, high within 30) closes the loop between detection and fix.
- **Compliance checks** — continuously verify controls against policy and regulation using policy-as-code tools so compliance state is always known, not discovered at audit time.

## A recommended introduction order

| Priority | Control | Why first |
|---|---|---|
| 1 | Secrets scanning (pre-commit + CI) | Prevents the single most common and damaging class of pipeline leak; near-zero false positives |
| 2 | SCA in CI | Finds known CVEs in dependencies with very low false-positive rates; often the largest immediate risk surface |
| 3 | Branch protection + SAST in PR | Gates new code, surfaces findings where developers can act immediately at lowest cost |
| 4 | IaC scanning | Catches the misconfiguration class of cloud breach before infrastructure is provisioned |
| 5 | Container scanning | Stops vulnerable base images reaching production; runs automatically at build time |
| 6 | DAST / IAST | Tests the running application from inside and outside; requires a test environment |
| 7 | SBOM + signing | Establishes supply-chain trust and meets emerging regulatory requirements (EU CRA, NIST guidance) |

Start with controls 1–3. They provide the highest risk reduction per implementation effort and build the cultural habit of security-in-CI before adding more sophisticated controls.

## A finding's journey through the pipeline

To understand how the pieces connect, follow a typical SAST finding from discovery to closure:

1. **Developer writes code** with a SQL string built by concatenation (potential injection). The IDE plugin (e.g., Semgrep LSP, Snyk IDE) flags it inline — the developer sees it before a single commit.
2. **Pre-commit hook** runs a fast Semgrep scan on staged files. If the developer ignored the IDE warning, the hook catches it before the commit lands.
3. **Pull request CI** runs a full SAST scan against the base branch. A PR comment is posted automatically with the finding, the file, the line, the CWE reference, and a remediation suggestion. The PR is blocked from merge until the finding is addressed.
4. **Developer fixes** the injection by using a parameterized query. They push an updated commit; the SAST re-runs and the gate passes.
5. **The fix is merged.** The scan result (pass, with the finding resolved) is automatically ingested into the vulnerability management platform (e.g., DefectDojo) via webhook, closing the finding ticket.
6. **Governance dashboard** shows the MTTR for this finding (time from PR open to fix merged), contributing to the team's remediation SLA metric.

This flow is fully automated. No security team member touched it. The developer was informed, guided, and unblocked within their normal workflow.

## Integration architecture

Tools in a DevSecOps pipeline connect through a few standard integration patterns:

- **CI hooks** — SAST, SCA, IaC, and secrets scanners run as pipeline steps. They emit exit codes (0 = pass, non-zero = fail) and produce structured output (SARIF, JSON, CycloneDX) consumed by downstream tooling.
- **SARIF ingestion** — GitHub Code Scanning, GitLab Security Dashboard, and DefectDojo all consume SARIF. A scanner that emits SARIF automatically integrates with any of these platforms without custom parsing.
- **Webhooks / APIs** — CI platforms push scan results to vulnerability management tools via webhook. Defect management tools (Jira, DefectDojo) create and close tickets via API. Dashboards pull from both.
- **OCI attestations** — SBOM and provenance attestations are stored as OCI artifacts alongside container images in the registry, discovered and verified by admission controllers at deploy time.
- **Policy engines** — OPA/Gatekeeper and Kyverno receive admission requests from Kubernetes and evaluate policies against them in real time. The decision (allow/deny) is logged for audit.

## Security gates without breaking flow

The goal is not to block every build on every finding — that destroys developer trust and creates alert fatigue. Instead:

- Gate on **risk** (severity, exploitability, reachability), not raw counts.
- Baseline existing issues so teams are accountable only for *new* risk they introduce. Many SAST tools support a `--baseline` flag or new-findings-only mode.
- Give developers actionable, in-context results in the tools they already use (IDE plugin, PR comment, Slack message) — not just a CI log they have to go digging for.
- Support a documented exception process for the rare cases where a finding cannot be remediated immediately, so teams do not disable gates as a workaround.

## Secure the pipeline, not just the app

CI/CD tooling expands your attack surface. Build runners, package registries, third-party Actions/plugins, and long-lived tokens are all attractive targets. Concrete hardening steps include:

- Use **OIDC workload identity** (GitHub OIDC → AWS/GCP/Azure) instead of long-lived cloud credentials stored as secrets.
- **Pin** third-party Actions and container images to immutable SHA digests, not mutable tags.
- **Restrict `permissions:`** blocks in GitHub Actions to the minimum required per job.
- Run jobs in **ephemeral, isolated runners** and restrict network egress to only what the build needs.
- Audit third-party plugin and Action updates; treat them as supply-chain risk.

See the [CI/CD Pipeline Security](../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-3-CICD-Pipeline-Security.md) page for a full hardening checklist.

## Maturity and frameworks

Use established frameworks to decide *what* to do and *how well*:

- [OWASP SAMM](https://owaspsamm.org/) — measure and improve security maturity across business functions.
- [OWASP DSOMM](https://dsomm.owasp.org/) — map concrete DevSecOps activities to maturity levels.
- [NIST SSDF (SP 800-218)](https://csrc.nist.gov/Projects/ssdf) — baseline secure-development practices for compliance.
- [SLSA](https://slsa.dev/) — supply-chain integrity levels.

See [Frameworks and Standards](0-3-Frameworks-and-Standards.md) for how these relate.
