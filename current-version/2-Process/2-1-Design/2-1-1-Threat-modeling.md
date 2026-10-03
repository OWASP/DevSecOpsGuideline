# Threat Modeling

Threat modeling is a structured way to find security problems in a **design** before any code is written — the earliest and cheapest point to fix them. By reasoning about what you are building and how it could be attacked, teams uncover design flaws that no scanner can detect, because scanners only see implementation, not intent.

The cost of finding a design flaw in a whiteboard session is negligible. The cost of discovering the same flaw in production — after an incident — is orders of magnitude higher. Threat modeling is the discipline that closes that gap.

## The four key questions

The [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/) frames the practice around four questions:

1. **What are we working on?** — diagram the system, data flows, and trust boundaries.
2. **What can go wrong?** — enumerate threats against each component and flow.
3. **What are we going to do about it?** — decide on mitigations for the threats that matter.
4. **Did we do a good enough job?** — review and validate the model and its mitigations.

These questions are intentionally methodology-agnostic — they work whether your team uses sticky notes, a whiteboard, a formal tool, or code-based models.

## Methodologies

- **STRIDE** — categorizes threats as Spoofing, Tampering, Repudiation, Information disclosure, Denial of service, and Elevation of privilege. Each element in your data-flow diagram is examined against each STRIDE category. A good general-purpose starting point.
- **PASTA** — a seven-stage, risk-centric process (Process for Attack Simulation and Threat Analysis) that ties threats to business impact. Better suited to mature programs with defined risk appetite.
- **LINDDUN** — focuses on **privacy** threats (Linkability, Identifiability, Non-repudiation, Detectability, Disclosure of information, Unawareness, Non-compliance). Use alongside STRIDE for applications handling personal data.
- **Attack trees** — model how an attacker could reach a goal step by step. Excellent for high-value targets or specific threat scenarios where you want to reason about attacker economics.
- **OCTAVE** — operationally focused, suitable for organizations analyzing risk at the process and asset level rather than the feature level.

## Building the data-flow diagram

The data-flow diagram (DFD) is the foundation. A minimal DFD identifies:

- **Processes** — components that transform or act on data (services, functions, jobs).
- **Data stores** — databases, caches, file systems, queues.
- **External entities** — actors outside the trust boundary (users, third-party services, partners).
- **Data flows** — how data moves between the above, including protocols and encryption status.
- **Trust boundaries** — lines across which data passes from a lower-trust to a higher-trust zone (or vice versa). Every crossing is a candidate threat.

Keep DFDs at the right level of abstraction: one diagram per service or bounded context is more useful than one giant diagram for the entire system.

## STRIDE applied — a worked example

For a REST API endpoint that accepts a user-uploaded file:

| STRIDE category | Threat example | Mitigation |
|---|---|---|
| Spoofing | Caller forges user identity in request header | Validate JWT on every request, never trust client-supplied identity fields |
| Tampering | File content modified in transit | Enforce TLS; verify file hash after upload |
| Repudiation | Uploader denies submitting malicious file | Log upload events with authenticated user ID and file hash |
| Information disclosure | Error message leaks server path or stack trace | Sanitize error responses; log details server-side only |
| Denial of service | Attacker uploads gigabyte files to exhaust storage | Enforce file size limits and upload rate limits |
| Elevation of privilege | File is stored in a path the web server executes | Store uploads outside the web root; scan before serving |

## Making it fit DevSecOps

Traditional threat modeling was a heavyweight, document-driven exercise done once. To keep pace with agile delivery:

- **Right-size it** — model the riskiest features and changes, not every story. A 30-minute whiteboard session beats a 40-page document nobody reads.
- **Do it continuously** — trigger a lightweight model update for any change that crosses a trust boundary, adds an external integration, or handles new categories of sensitive data.
- **Threat-model as code** — express models in version-controlled, diffable formats ([pytm](https://github.com/OWASP/pytm), [threagile](https://threagile.io/)) so they evolve with the system and integrate into CI pipelines for automated risk reporting.
- **Make it collaborative** — involve developers, architects, product managers, and security champions; the conversation is often more valuable than the artifact itself.
- **Close the loop** — every identified threat should produce a ticket in the backlog. Unmitigated threats should have an explicit risk-acceptance decision, not be silently ignored.

## When to threat model

| Trigger | Scope |
|---|---|
| New service or major feature | Full model of the new component and its integrations |
| New external integration | Trust boundary analysis for the integration and its data |
| Authentication or authorization change | Focused STRIDE analysis on identity and access paths |
| Post-incident review | Update existing model to reflect how the attacker actually moved |
| Periodic refresh | Annual or semi-annual full model review |

## Common pitfalls

- **Modeling too late** — threat modeling *after* code is written captures fewer high-impact findings and produces expensive rework. Start during design.
- **Doing it alone** — security-team-only threat models miss the developer's knowledge of implementation nuance. Threat modeling is a team sport.
- **Treating it as a one-time gate** — a threat model written at project kickoff and never updated is misleading, not helpful.
- **Producing threats without owners** — every threat that warrants action must have an assigned owner and a ticket. Unowned threats disappear.
- **Ignoring the "did we do a good enough job?" question** — review your threat model against actual test results and penetration findings to calibrate model quality over time.

## Metrics

- Number of threat-modeled features per quarter vs total features shipped.
- Average threats identified per model (rising over time suggests improving depth; sudden drops suggest model quality degraded).
- Percentage of modeled threats with closed mitigations within the sprint.
- Vulnerabilities discovered in production that were not in the threat model (escape rate — a calibration metric).

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Ad-hoc whiteboard sessions for highest-risk features; output is a list of threats in the backlog |
| Developing | STRIDE applied consistently to all new features crossing trust boundaries; DFDs stored in the repo |
| Defined | Threat-model-as-code (pytm or threagile) integrated into CI; model reviews at sprint milestones |
| Advanced | Automated threat generation from architecture diagrams; threat model findings correlated with SAST/DAST/pentest findings |

---

## Tools[^1]

### Open-source

- [OWASP pytm](https://github.com/OWASP/pytm) — A Python-based framework for expressing threat models as code. Generates DFDs, sequence diagrams, and STRIDE reports from a Python definition file. Integrates into CI.
- [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/) — Free, open-source threat modeling tool with a visual DFD editor and STRIDE categorization. Stores models as JSON for version control.
- [OWASP ThreatAtlas](https://github.com/OWASP/ThreatAtlas) — A community-maintained, structured knowledge base of real-world threats mapped to attack patterns, MITRE ATT&CK techniques, and mitigations. Where Threat Dragon helps you *create* a model, ThreatAtlas helps you *populate* it with curated, evidence-based threat intelligence drawn from documented incidents. Use it during the "what can go wrong?" phase to ensure your threat library reflects the actual attacker landscape rather than only theoretical concerns.
- [Threagile](https://threagile.io/) — Agile, YAML-based threat modeling. Takes a YAML model of your architecture and outputs a risk report with data-flow diagrams. Designed for CI integration.
- [Attack Flow](https://center-for-threat-informed-defense.github.io/attack-flow/) — MITRE CTID project for modeling sequences of adversary actions using ATT&CK techniques. Useful for post-incident and red team threat analysis.

### Commercial

- [IriusRisk](https://www.iriusrisk.com/) — Automated threat modeling platform with rules-based threat generation from architecture questionnaires. Integrates with Jira for backlog creation.
- [SD Elements](https://www.securitycompass.com/sdelements/) — Combines threat modeling with security requirements management; generates tasks directly into the development backlog.
- [Microsoft Threat Modeling Tool](https://aka.ms/threatmodelingtool) — Free from Microsoft; focuses on DFD-based STRIDE analysis. Best suited to Microsoft-stack environments.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [Threat Modeling Manifesto](https://www.threatmodelingmanifesto.org/)
- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP ThreatAtlas](https://github.com/OWASP/ThreatAtlas)
- [Adam Shostack — Threat Modeling: Designing for Security](https://www.wiley.com/en-us/Threat+Modeling%3A+Designing+for+Security-p-9781118809990)
- [STRIDE per Element — Microsoft Security Blog](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
