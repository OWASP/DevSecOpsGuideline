# Incident Response and Detection Engineering

Every control in this guideline reduces the likelihood of an incident, none eliminates it. What separates a contained event from a breach is how quickly you detect it and how well-practiced the response is. **Incident Response (IR)** is the discipline of preparing for, handling, and learning from incidents; **Detection Engineering** is the practice of building and maintaining the detections that tell you an incident is happening, treating them as tested, versioned software rather than one-off alert rules.

DevSecOps adds a specific twist: many modern incidents originate in the delivery pipeline itself — a leaked token in a repository, a compromised CI runner, a poisoned dependency — and the lessons learned should flow back into the pipeline as new gates, rules, and tests.

## IR lifecycle: NIST SP 800-61 Rev. 3

[NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final) (April 2025) supersedes Rev. 2 and re-frames incident response around the six functions of the NIST Cybersecurity Framework 2.0 rather than the older four-phase cycle:

| CSF 2.0 function | Role in incident response |
|---|---|
| **Govern, Identify, Protect** | Preparation: policy, roles, asset inventory, risk assessment, and controls that prevent or reduce incidents |
| **Detect** | Find and analyze possible incidents from monitoring and reports |
| **Respond** | Triage, contain, eradicate, communicate, and document |
| **Recover** | Restore services and verify normal operation |
| **Improvement** (within Identify) | Lessons learned feed back into every function |

The practical takeaway: preparation and improvement are continuous, not bookends. Detection engineering and pipeline hardening are part of the incident response program.

## Cloud and CI/CD incident types

Standard enterprise playbooks often miss the incidents DevSecOps teams actually face. Prepare specific runbooks for at least:

- **Leaked secret** — API key, cloud credential, or token exposed in a repository, log, or container image.
- **Compromised CI/CD pipeline** — malicious workflow change, stolen runner or pipeline token, tampered build artifact. See [CI/CD Pipeline Security](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-3-CICD-Pipeline-Security.md).
- **Compromised dependency or base image** — a malicious or backdoored package or image version consumed by your builds.
- **Cloud account or role compromise** — suspicious use of a workload identity or access key, unexpected resource creation.
- **Exploited internet-facing vulnerability** — especially one on the CISA KEV catalog.

### Example: leaked secret runbook

1. **Triage** — confirm the secret is valid and identify its owner, scope, and where it was exposed (public repository, private fork, build log, image layer).
2. **Contain** — revoke or rotate the credential immediately; rotating is the priority, history rewriting is secondary because the secret must be assumed already copied.
3. **Scope** — query audit logs (for example CloudTrail or the provider's equivalent) for all activity by that credential since exposure; look for new identities, keys, and persistence.
4. **Eradicate and recover** — remove the secret from code and history, rebuild affected artifacts, and redeploy with a new credential issued through a secret manager or workload identity.
5. **Learn** — add or tune [pre-commit and CI secret scanning](../2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md), and move the workload to short-lived credentials where possible.

### Example: compromised dependency runbook

1. Identify affected artifacts using [SBOMs](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) — which builds and running workloads include the component and version.
2. Freeze deployments of affected services and block the version in your artifact proxy or registry.
3. Rotate secrets accessible to affected builds and workloads; review build logs for unexpected network egress.
4. Rebuild from a known-good version, verify provenance, and redeploy.

## Runbooks and SOAR

- Write runbooks as **short, executable checklists** with an owner, entry criteria, decision points, and required evidence. Store them in version control next to the code they protect.
- Automate the repeatable, low-risk steps first: enrich an alert with asset and owner data, open a ticket, disable a leaked key, quarantine a workload. Keep human approval for destructive or business-impacting actions.
- **SOAR** (Security Orchestration, Automation, and Response) platforms or simple workflow tools tie alerts to these steps. Start with a handful of high-volume cases rather than attempting a full automation catalog.
- Pre-define **communication paths**: who declares an incident, who talks to legal, customers, and regulators, and how the response team coordinates if the normal chat or ticketing tool is itself compromised.
- Run **tabletop exercises** at least twice a year using the real scenarios above, including a pipeline compromise.

## Detection-as-code with Sigma

Detections should be reviewed, versioned, tested, and deployed the same way as application code.

- **Sigma** is an open, vendor-neutral rule format for log-based detections. Rules are written once in YAML and converted to the query language of your SIEM or log platform using `pySigma` backends and the `sigma-cli` tool.
- Keep rules in a Git repository with pull-request review and CI checks (syntax validation, required metadata, ATT&CK tagging).

```yaml
title: Cloud Access Key Created for Existing User
status: experimental
description: Detects creation of an access key, a common persistence step after credential theft
logsource:
  product: aws
  service: cloudtrail
detection:
  selection:
    eventSource: iam.amazonaws.com
    eventName: CreateAccessKey
  condition: selection
falsepositives:
  - Legitimate key rotation by automation or administrators
level: medium
tags:
  - attack.persistence
  - attack.t1098.001
```

```bash
# Validate rules and convert for a target backend in CI
sigma check rules/
sigma convert -t splunk -p splunk_cim rules/cloud/
```

(Backend and pipeline names depend on the installed pySigma plugins; check the plugin documentation for your platform.)

## Testing detections

A detection that has never fired is an assumption, not a control.

- **Unit-test rules** against sample log events: one known-malicious event that must match and benign events that must not.
- **Replay recorded telemetry** (for example from a past incident or a test account) through the pipeline to verify parsing, field mappings, and routing end to end.
- **Emulate the technique** with tools such as Atomic Red Team or Stratus Red Team, and verify the alert fires, carries useful context, and reaches the right queue. See [Breach and Attack Simulation](2-7-6-Breach-and-attack-simulation.md).
- Re-run detection tests on a schedule and after every log source, schema, or rule change to catch regressions.

## The purple-team loop

1. Choose a technique relevant to your incident history or threat intelligence (for example, abuse of CI runner credentials).
2. Execute it in a controlled way; blue team observes in real time.
3. Record the outcome: prevented, detected, logged but not alerted, or invisible.
4. Write or tune the detection, then re-execute to confirm.
5. Merge the rule through the normal review process and add the test to the regression suite.

## Post-incident review and feedback to the pipeline

A blameless post-incident review is only valuable when it produces tracked changes:

- **Root cause and contributing factors** — including the control that should have prevented or detected it and why it did not.
- **Detection gaps** — new rules, new log sources, or retention changes, tracked in the detection engineering backlog.
- **Pipeline changes** — new [security gates](../2-3-Build/2-3-5-Security-Gates.md), scanner rules, policy-as-code checks, or hardened defaults that make the same class of incident harder to repeat.
- **Process changes** — runbook fixes, missing contacts, unclear decision rights.
- Assign each action an owner and a due date, and review completion in the next security meeting. Feed the finding into [vulnerability management](2-7-4-Vulnerability-Management.md) and the [logging and monitoring](2-7-2-Logging-and-Monitoring.md) roadmap.

## Common pitfalls and anti-patterns

- **Runbooks that exist only in a wiki nobody opens** — untested playbooks fail under pressure; practice them.
- **Rotating nothing after a leak** — deleting a commit does not revoke a credential.
- **Detections as unreviewed console edits** — no version history, no tests, no owner, so rules rot silently.
- **Alert volume without triage quality** — noisy rules train analysts to ignore alerts; track and tune false positives.
- **Treating CI/CD as out of scope for IR** — pipeline logs and runner telemetry are rarely collected, so pipeline compromises go undetected.
- **Over-automating containment** — automated actions without guardrails can cause outages; scope and approve them.
- **Lessons learned with no follow-through** — review documents that never become tickets.

## Maturity progression

**Starter** — Written incident response plan with named roles and contacts. Runbooks for leaked secrets and compromised cloud credentials. Audit logging enabled for cloud accounts and the source control platform.

**Intermediate** — Runbooks for pipeline and dependency compromise, tested by tabletop exercises. Detection rules stored in Git with peer review. Basic SOAR automation for enrichment and ticketing. Post-incident reviews tracked to closure.

**Advanced** — Sigma-based detection-as-code pipeline with unit tests and replay testing. Regular purple-team cycles driven by [BAS](2-7-6-Breach-and-attack-simulation.md) and threat intelligence. Automated containment with guardrails for well-understood cases. Incident lessons systematically converted into pipeline gates and measured for recurrence.

## Metrics and KPIs

- **Mean time to detect (MTTD)** and **mean time to respond/contain (MTTR)** — tracked by incident type, including secret-leak and pipeline incidents.
- **Time to revoke a leaked credential** — from detection to confirmed rotation.
- **Detection coverage** — percentage of prioritized ATT&CK techniques with a tested detection.
- **Detection test pass rate** — percentage of rules whose tests pass on the latest run; regressions should be zero.
- **False positive rate** per rule and analyst time per alert.
- **Post-incident action closure rate** — percentage of review actions completed by their due date.
- **Repeat incident rate** — incidents with the same root cause as a previous one.
- **Runbook exercise cadence** — scenarios exercised in the last 12 months versus planned.

---

## Tools[^1]

### Open-source

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) — Library of small ATT&CK-mapped tests for validating that detections fire.
- [Falco](https://github.com/falcosecurity/falco) — CNCF runtime threat detection for containers, hosts, and Kubernetes, with rules as code.
- [Shuffle](https://github.com/Shuffle/Shuffle) — Open-source SOAR platform with a visual workflow builder and many app integrations.
- [Sigma](https://github.com/SigmaHQ/sigma) — Vendor-neutral detection rule format and community rule repository, used with [pySigma](https://github.com/SigmaHQ/pySigma) and [sigma-cli](https://github.com/SigmaHQ/sigma-cli) to convert and validate rules.
- [Stratus Red Team](https://github.com/DataDog/stratus-red-team) — Cloud attack techniques for AWS, Azure, GCP, and Kubernetes to test cloud detections.
- [TheHive](https://github.com/TheHive-Project/TheHive) — Case management platform for security incident response; check the project for current licensing and edition details before adopting.
- [VECTR](https://github.com/SecurityRiskAdvisors/VECTR) — Tracks purple-team exercises and detection outcomes over time.

### Commercial

- [Cortex XSOAR](https://www.paloaltonetworks.com/cortex/cortex-xsoar) — SOAR platform with playbook automation and case management.
- [Elastic Security](https://www.elastic.co/security) — SIEM and detection platform with a detection-rules repository and Sigma-convertible rule workflows.
- [Google Security Operations](https://cloud.google.com/security/products/security-operations) — Cloud SIEM and SOAR with detection rules as code.
- [Microsoft Sentinel](https://learn.microsoft.com/azure/sentinel/) — Cloud-native SIEM and SOAR with analytics rules deployable through repositories.
- [Splunk Enterprise Security](https://www.splunk.com/en_us/products/enterprise-security.html) — SIEM with detection content, SOAR integration, and risk-based alerting.
- [Tines](https://www.tines.com/) — No-code workflow automation platform widely used for security orchestration.

---

### Links

- [NIST SP 800-61 Rev. 3](https://csrc.nist.gov/pubs/sp/800/61/r3/final)
- [Sigma detection format documentation](https://sigmahq.io/docs/guide/getting-started.html)
- [MITRE ATT&CK](https://attack.mitre.org/)

[^1]: Listed in alphabetical order.
