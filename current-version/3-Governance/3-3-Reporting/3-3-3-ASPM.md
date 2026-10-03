# Application Security Posture Management (ASPM)

As organizations adopted dozens of security scanners, they discovered a new problem: a flood of disconnected findings with no shared context, no deduplication, and no way to tell which issues actually matter. **Application Security Posture Management (ASPM)** answers this by continuously collecting, correlating, and contextualizing security data from across the entire software lifecycle — from source control to build to runtime — to maintain a single, live picture of application risk.

## ASPM data model

An ASPM platform ingests and normalizes data from many sources:

| Data source | What it contributes |
|---|---|
| SAST scanners | Code-level vulnerability findings with file, line, and CWE |
| SCA scanners | Dependency CVEs with PURL, CVSS, and ecosystem |
| DAST scanners | Runtime-discovered vulnerabilities with URL, method, and evidence |
| Container scanners | Image CVEs with package name and layer |
| IaC scanners | Misconfiguration findings with resource type and policy ID |
| Secrets scanners | Secret types, locations, and exposure risk |
| SBOM feeds | Component inventory per artifact/service |
| Runtime telemetry | Which code paths are executed in production |
| Source control metadata | Repository, team, branch protection, last commit |
| Asset inventory | Service criticality, data classification, internet exposure, compliance scope |
| CISA KEV / EPSS | Real-world exploitability signals for prioritization |

Each finding is normalized to a common schema: vulnerability identifier, affected asset, severity, source tool, discovery time, assigned owner, SLA status, and remediation state. This normalization is what makes cross-tool deduplication and comparison possible.

## How ASPM deduplicates findings

The same underlying vulnerability is routinely flagged by multiple tools. Without deduplication, a team sees three separate tickets with three separate fix requests:

**Example: SQL injection in `UserRepository.java`, line 42**

| Tool | Finding ID | Title | Severity |
|---|---|---|---|
| Semgrep (SAST) | SG-1041 | SQL injection via string concat | HIGH |
| Snyk Code (SAST) | SC-8822 | Unsanitized input in JDBC query | HIGH |
| Burp Suite (DAST) | BS-331 | SQL injection confirmed in `/api/users` | CRITICAL |

Without ASPM: three separate tickets, three separate remediation requests, possible triple-counting in metrics.

With ASPM deduplication:
1. Normalize all three to CWE-89 (SQL Injection).
2. Match by asset (`UserRepository.java`) and finding type (CWE-89).
3. Merge into one finding with three source references.
4. Elevate severity to CRITICAL (Burp confirmed it at runtime).
5. Assign to the owning team once; track one remediation workflow.

The result: one actionable finding, higher-confidence severity (runtime confirmation), and accurate metrics that do not triple-count the same issue.

## ASPM vs SIEM vs vulnerability management platform

These three categories are often confused:

| Platform | Primary purpose | Data it processes | Who uses it |
|---|---|---|---|
| **SIEM** | Security operations, threat detection, incident response | Logs, events, alerts, network flows | SOC analysts, IR teams |
| **Vulnerability Management** | Track and remediate infrastructure CVEs | Network scan results, agent-based CVEs, OS patches | IT security, sysadmins |
| **ASPM** | Application risk across the SDLC | SAST, SCA, DAST, container, IaC, SBOM, runtime | AppSec, development teams, security engineers |

SIEM detects threats in real time using events. Vulnerability management tracks known exposures in infrastructure. ASPM manages risk in *applications* — the code, its dependencies, its containers, and its pipelines — with the developer team as the primary consumer.

ASPM and SIEM are complementary: ASPM feeds enriched application risk context to the SIEM (which service has a known unpatched critical CVE currently exposed to the internet?), while the SIEM feeds runtime threat signals back to ASPM (this service is actively being probed — elevate its risk priority).

## Risk score normalization across tools

Different tools use different severity scales:
- CVSS (0–10 numeric)
- SAST tool-specific: Critical / High / Medium / Low
- DAST tools: P1 / P2 / P3 / P4
- Cloud scanners: Critical / High / Medium / Low / Informational

ASPM normalizes these to a common scale using:
1. **Base severity** — mapped to a common 4-level scale (Critical / High / Medium / Low).
2. **EPSS enrichment** — the probability this specific CVE is exploited in the wild within 30 days (0–100%). High EPSS elevates priority.
3. **CISA KEV** — if the CVE is on the Known Exploited Vulnerabilities catalog, it is treated as Critical regardless of CVSS.
4. **Reachability** — if the vulnerable code path is confirmed unreachable, the finding is deprioritized even if CVSS is high.
5. **Asset context** — internet-facing, PII-handling, or in-scope for PCI/HIPAA services carry a risk multiplier.

The final risk score drives gate decisions, SLA assignment, and dashboard ranking — giving teams a single defensible prioritization that is consistent across all tools.

## What ASPM does

- **Aggregates and deduplicates** findings from SAST, SCA, secrets, IaC, DAST, container, and runtime tools into a single normalized inventory.
- **Correlates across the lifecycle** — links a finding in code to the build it shipped in and the workload running it in production.
- **Adds code-to-runtime context** — knows whether vulnerable code is reachable from an external entry point, whether the asset is internet-facing, what data classification it touches, and which team owns it.
- **Prioritizes by real risk** — combines CVSS, EPSS, CISA KEV, reachability, business criticality, and runtime exposure.
- **Maps ownership** — connects each risk to the team, service, and individual responsible, enabling direct assignment and accountability.

## Why it matters

Traditional scanning produces *findings*; ASPM produces *prioritized, owned, contextual risk*. This directly addresses the biggest failure mode of AppSec programs — **alert fatigue** — by cutting thousands of raw findings down to the few that are exploitable and reachable.

A concrete example: a CVE with CVSS 9.8 in a logging library used only in a dev tool, with no network exposure, may rank below a CVSS 7.2 CVE in an auth service that is internet-facing and holds PII — because ASPM applies reachability and asset context that raw CVSS cannot.

## ASPM for executive reporting

ASPM is the primary data source for AppSec program reporting to leadership:

**Executive dashboard (monthly):**
- Risk trend: total critical/high findings, open vs closed, week-over-week delta.
- Mean time to remediate (MTTR) by severity, by team, vs SLA target.
- Escape rate: findings discovered post-merge vs pre-merge (measures shift-left effectiveness).
- Risk by business unit or product line: which services carry the most unresolved risk.
- Compliance posture: percentage of in-scope services meeting security gate requirements.

This is reportable in a single dashboard because ASPM aggregates from all sources. Without ASPM, this data must be manually compiled from 5–10 tool consoles, introducing inconsistency and lag.

## Active vs passive ASPM

- **Passive ASPM** aggregates and correlates findings into a unified view, provides prioritization, assigns ownership, and tracks remediation. This is the evolution of the [central vulnerability dashboard](3-3-2-Central-vulnerability-management-dashboard.md) — the same data, with much richer context.
- **Active ASPM** goes further: it continuously monitors posture, orchestrates scanners (triggering targeted scans when code changes), enforces policy (feeding [Security Gates](../../2-Process/2-3-Build/2-3-5-Security-Gates.md)), and drives remediation — increasingly with AI agents that triage, prioritize, propose fixes, or open pull requests with minimal human intervention.

## Buy vs build

**Build considerations:**
- Connecting 10+ scanner outputs with normalization, deduplication, and custom enrichment requires significant engineering — typically a 2–4 person-year initial investment.
- Open-source tools (DefectDojo) can get 60% of the way there; the remaining 40% (reachability, EPSS integration, runtime correlation) requires custom development.
- Best suited for organizations with a large AppSec engineering team and strong data engineering capability.

**Buy considerations:**
- Commercial ASPM platforms (Apiiro, ArmorCode, Cycode, Legit Security) offer pre-built integrations for 100+ scanners, reachability analysis, and executive dashboards out of the box.
- Time-to-value is typically 4–8 weeks vs 6–18 months to build equivalent capability.
- Best suited for organizations that want to focus engineering capacity on remediation, not tooling.

**Recommendation:** Start with DefectDojo for passive aggregation (free, immediate value). Evaluate commercial ASPM when you have 5+ scanner sources, more than 2 AppSec engineers, and are measuring false positive rates systematically.

## How ASPM processes findings

```
Scanner A (SAST)  ──┐
Scanner B (SCA)   ──┤
Scanner C (DAST)  ──┤──> Normalization ──> Deduplication ──> Enrichment ──> Prioritized Risk
Scanner D (runtime)─┤                                         (reachability,      ──> Ownership
SBOM feeds        ──┘                                          EPSS, KEV,          ──> Workflow
                                                               asset context)
```

## Where ASPM fits in this guideline

ASPM is the connective tissue across the pillars: it consumes the output of every Process-stage control and applies Governance-level prioritization and policy:

- **People** — maps findings to owning teams; feeds developer-facing dashboards with actionable, high-signal work.
- **Process** — drives [Security Gates](../../2-Process/2-3-Build/2-3-5-Security-Gates.md) with correlated risk; feeds [Vulnerability Management](../../2-Process/2-7-Operate/2-7-4-Vulnerability-Management.md) with prioritized queues.
- **Governance** — provides the structured evidence for [Compliance Auditing](../3-1-Compliance-Auditing/3-1-1-Compliance-Auditing.md) and the posture trends for [Tracking Maturities](3-3-1-Tracking-maturities.md).

ASPM is how mature programs move from "running scanners" to "managing risk."

## Maturity progression

**Starter** — Individual scanner consoles, manual aggregation in a spreadsheet. Risk assessment is tool-specific and inconsistent.

**Intermediate** — Central vulnerability management platform (DefectDojo, Dependency-Track) aggregating 5+ scanners. Deduplication configured. Ownership assigned. SLAs tracked. Executive dashboard published monthly.

**Advanced** — Dedicated ASPM platform with full code-to-runtime correlation, reachability analysis, and EPSS/KEV enrichment. Security gates driven by ASPM output. AI-assisted triage and fix suggestions. Real-time posture dashboard for leadership. All compliance evidence auto-collected from ASPM data.

## Common pitfalls

- **Treating ASPM as a scanner** — ASPM needs data from many scanners to be effective. An ASPM with inputs from only two tools cannot produce meaningful correlation.
- **Skipping normalization** — feeding raw scanner severity levels without normalizing produces skewed prioritization.
- **No code-to-runtime linkage** — an ASPM that only aggregates static findings without runtime context is a better spreadsheet, not posture management.
- **ASPM owned by security only** — if development teams cannot see and act on ASPM output directly, it becomes another security reporting tool rather than a shared risk management layer.
- **Not tracking false positive rate** — if ASPM is not reducing noise vs. raw scanner output, the enrichment and deduplication are not working. Measure and improve.

## Metrics

| Metric | What it tells you |
|---|---|
| Mean time from finding to contextual prioritization | How quickly the platform enriches and ranks incoming findings |
| % of critical findings with reachability data | Depth of ASPM enrichment coverage |
| Risk reduction rate (findings closed / findings opened, per week) | Net direction of the overall risk posture |
| Findings with no assigned owner | Governance gaps; unowned findings rarely get fixed |
| False positive rate post-ASPM enrichment vs. raw scanner output | Value the platform adds in noise reduction |
| Coverage: % of services with ASPM data | Blind spots in the posture picture |
| Executive dashboard published on schedule | Governance discipline indicator |

---

## Tools[^1]

### Open-source

- [OWASP DefectDojo](https://www.defectdojo.org/) — Findings aggregation and management with ASPM-adjacent capabilities: deduplication, SLA tracking, ownership, workflow integration, and rich API. The most accessible entry point for passive ASPM. Does not natively provide reachability analysis but integrates well with tools that do. Best first step for any team moving beyond per-tool consoles.

### Commercial

- [Apiiro](https://apiiro.com/) — Code-to-runtime application risk and ASPM. Builds a risk graph from code structure, secrets, PII handling, and logic changes through to runtime exposure. Strong risk-based code review prioritization.
- [ArmorCode](https://www.armorcode.com/) — ASPM platform aggregating and prioritizing findings across 100+ security tools. AI-assisted triage, SLA tracking, and bi-directional Jira integration. Strong for large enterprises managing many product teams.
- [Cycode](https://cycode.com/) — Complete ASPM across the software supply chain: source control, CI/CD, registries, and runtime. SBOM-anchored risk graph and code-to-production traceability.
- [Legit Security](https://www.legitsecurity.com/) — ASPM and software factory security posture. Focuses on pipeline and developer security risk alongside application findings.

---

### Links

[^1]: Listed in alphabetical order.
