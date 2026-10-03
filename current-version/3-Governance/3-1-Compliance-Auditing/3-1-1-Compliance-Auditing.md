# Compliance Auditing

Compliance auditing demonstrates — to regulators, customers, and leadership — that your security controls exist, work, and are followed. In a DevSecOps context the goal is to make compliance a **byproduct of good engineering** rather than a separate, manual scramble before each audit. When controls are automated and evidence is generated continuously, audits become a query against existing data instead of a fire drill.

## Common frameworks and regulations

Most organizations map their controls to one or more of:

- **SOC 2** — trust services criteria, common for SaaS. Requires evidence of access control, availability, and monitoring over a defined audit period (typically 12 months for Type II).
- **ISO/IEC 27001** — information security management system standard. Requires a risk-based approach and documented controls with ongoing review.
- **PCI DSS v4** — for handling payment card data. Highly prescriptive; now emphasizes continuous monitoring and customized implementation paths.
- **NIST SSDF (SP 800-218)** — secure software development practices; increasingly required for vendors selling to US federal agencies (per OMB M-23-16).
- **NIST 800-53** — comprehensive control catalog for federal and high-assurance environments.
- **HIPAA** — healthcare data; focuses on PHI safeguards, breach notification, and business associate agreements.
- **GDPR / PIPEDA / LGPD** — privacy-first regulations governing personal data of EU, Canadian, and Brazilian residents (see [Data Protection](../3-2-Data-protection.md)).
- **EU Cyber Resilience Act (CRA)** — security requirements for products with digital elements, including SBOMs and vulnerability disclosure obligations by 2027.
- **FedRAMP** — US federal cloud authorization, based on NIST 800-53 with strict continuous monitoring requirements.

## Continuous compliance vs. point-in-time audit

The traditional audit model is point-in-time: an auditor arrives, requests evidence for the past 12 months, and assesses controls as of the audit date. Controls can pass an annual audit while being violated for months between cycles.

Continuous compliance inverts this: controls are verified automatically on every change, evidence is collected and timestamped by the pipeline, and compliance state is always known. The audit becomes a reporting exercise, not an investigation.

| Dimension | Point-in-time audit | Continuous compliance |
|---|---|---|
| When | Annually or on-demand | Every commit, deploy, or config change |
| Evidence collection | Manual, retrospective scramble | Automated, real-time pipeline output |
| Drift detection | Found only at audit time | Immediate alert on deviation |
| Audit prep cost | High (weeks of effort) | Low (report export) |
| Ongoing assurance | Low (gaps possible between cycles) | High (continuous verification) |

## Compliance as code and continuous compliance

The modern approach automates the audit lifecycle end-to-end:

- **Map controls to checks** — express each control as an automated test wherever possible: a scan policy, a configuration assertion, a CI gate, or an admission rule. Document the mapping explicitly (control ID → automated check) so auditors can trace evidence to requirements.
- **Continuous Control Monitoring (CCM)** — verify controls on every commit, deploy, or configuration change rather than at quarterly audit time. Drift is caught and reported immediately.
- **Automated evidence collection** — pipelines emit logs, scan results, approvals, signed provenance, and attestations automatically. Store them in a tamper-resistant evidence vault for the audit period.
- **Policy as code** — encode compliance rules in machine-readable form and enforce them in CI and at admission (see [Policy as Code](3-1-2-Policy-as-code.md)).
- **Cross-framework mapping** — a single automated check often satisfies multiple frameworks simultaneously. Platforms like Drata and Vanta maintain pre-built control mappings so a passing SAST gate can satisfy both SOC 2 CC7.1 and NIST 800-53 SA-11 at once.

## What auditors actually look for

Understanding what evidence auditors request makes it easier to generate that evidence continuously:

| Evidence type | What it demonstrates | How to generate it automatically |
|---|---|---|
| Change management records | Every change was reviewed and approved | PR merge history with required reviewers; GitOps PR approvals |
| Vulnerability scan reports | Controls are active and findings are actioned | CI/CD scan outputs retained per pipeline run; DefectDojo audit trail |
| Access control review | Least-privilege principle is enforced | IAM access reviews via cloud-native tools; quarterly role review records |
| Security training completion | All staff received required training | LMS completion export (KnowBe4, Proofpoint) |
| Incident response records | Incidents are detected, tracked, and closed | SIEM alert-to-ticket lifecycle in Jira/ServiceNow |
| SBOM / dependency inventory | Software components are known and managed | Syft/CycloneDX SBOM attached to every release artifact |
| Penetration test report | External validation of controls | Annual pentest report with remediation status |
| Signed commits / provenance | Changes are attributable; artifacts are tamper-evident | Signed commits in git; cosign/SLSA attestations in registry |

## SOC 2 control mappings — examples

SOC 2 Trust Services Criteria (CC) map naturally to DevSecOps practices:

| SOC 2 criterion | DevSecOps practice | Evidence |
|---|---|---|
| CC6.1 — logical access controls | Branch protection, RBAC in CI/CD, MFA enforced | IAM config, branch protection settings |
| CC6.6 — restrict access to change management | Required reviewer rules; protected branches | GitHub/GitLab audit log of merges |
| CC7.1 — detect and monitor security events | SIEM with defined detection rules | SIEM alert log, detection-as-code policy files |
| CC7.2 — monitor system components | Continuous vulnerability scanning | Scan results per pipeline run, registry re-scan cadence |
| CC8.1 — manage changes | GitOps pull-request workflow with approvals | PR merge history, change management ticket links |
| A1.2 — availability risk mitigations | Capacity monitoring, health checks, progressive delivery | Monitoring dashboards, runbooks, deployment config |

## Audit trails

Auditability depends on tamper-resistant records of who did what and when:

- **GitOps as a change-management trail** — every infrastructure and configuration change is a reviewed, merged pull request with a complete history. This is inherently auditable and maps directly to SOC 2 CC8.1 and NIST 800-53 CM-3.
- **Signed commits and provenance** — signed commits prove who authored changes; signed build provenance proves what source produced which artifact (see [Artifact Signing](../../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md)).
- **Centralized, retained logs** — SIEM logs with defined retention periods (typically 1 year for SOC 2, 7 years for some regulated industries) support both investigation and evidence requests (see [Logging and Monitoring](../../2-Process/2-7-Operate/2-7-2-Logging-and-Monitoring.md)).
- **Release approvals and ticket links** — tie each release to an approved change ticket, capturing the human sign-off that automated processes cannot replace.

## Maturity progression

**Starter** — manual control documentation and periodic (annual) evidence collection per audit cycle. Controls exist but are not automated.

**Intermediate** — controls mapped to automated checks in CI. Evidence collection is partially automated (scan outputs saved, logs retained). Compliance is tracked against a known framework with quarterly reviews.

**Advanced** — continuous control monitoring with real-time drift detection. All audit evidence is auto-collected, indexed, and retrievable on demand. A single set of automated checks satisfies multiple frameworks simultaneously. Audit prep is a report export, not a project.

## Common pitfalls

- **Evidence collected only at audit time** — auditors can and do ask for historical evidence; collecting it retrospectively is stressful and unreliable. Type II auditors specifically look for evidence *over the period*, not just at a point in time.
- **Controls that exist on paper but not in practice** — an automated check will surface this; a policy document will not. Automate to keep documentation honest.
- **Framework sprawl without rationalization** — chasing every framework independently creates massive duplication. Map controls to a primary framework and cross-reference others. One passing CI gate can satisfy SOC 2, NIST, and ISO requirements simultaneously.
- **Treating compliance as the goal** — compliance is a floor, not a ceiling. Passing an audit does not mean you are secure; it means your controls met the criteria at the time of review. Design for real-world adversaries, not just auditor checklists.

## Metrics

| Metric | What it tells you |
|---|---|
| % of controls with automated checks | How much of your compliance posture is continuously verified vs. manually attested |
| Days to gather audit evidence | A proxy for automation maturity; target should be hours, not weeks |
| Control drift rate | How often automated checks detect a configuration falling out of compliance |
| Open compliance findings by severity | Current gap between actual and required posture |
| Time since last framework review | Controls age; frameworks update and so should your mapping |

## Make it sustainable

Treat compliance as continuous, not annual. Tooling can map a single control to multiple frameworks (test once, satisfy many), reducing duplicated effort. The aim is that passing an audit and running a secure pipeline are the same activity.

---

## Tools[^1]

### Open-source

- [Cloud Custodian](https://cloudcustodian.io/) — rules engine for cloud governance; write YAML policies to detect and auto-remediate non-compliant cloud resources. Best for teams already living in cloud config.
- [OpenSCAP](https://www.open-scap.org/) — compliance scanning against SCAP/XCCDF baselines including CIS and DISA STIGs. Strong for OS-level compliance in regulated environments.
- [Open Policy Agent](https://www.openpolicyagent.org/) — general-purpose policy engine for codifying compliance rules in Rego. Use to gate CI, Kubernetes admission, and API authorization.

### Commercial

- [Drata](https://drata.com/) — continuous compliance automation for SOC 2, ISO 27001, HIPAA, PCI DSS, and more. Integrates with cloud providers, code platforms, and HR systems to auto-collect evidence.
- [Vanta](https://www.vanta.com/) — automated compliance and trust management; strong on cross-framework coverage and vendor risk management.
- [Secureframe](https://secureframe.com/) — compliance automation with built-in security training, risk management, and vendor questionnaire management.

---

### Links

[^1]: Listed in alphabetical order.
