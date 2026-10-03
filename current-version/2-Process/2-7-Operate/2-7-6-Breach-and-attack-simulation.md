# Breach and Attack Simulation

Having security controls is not the same as knowing they work. **Breach and Attack Simulation (BAS)** continuously and safely emulates real adversary techniques against your environment to validate whether your defenses actually detect and prevent them. Where a pentest is a point-in-time snapshot, BAS provides ongoing, automated assurance that controls have not silently drifted or broken.

Security controls fail silently all the time: a SIEM rule that fired correctly six months ago may have stopped working after a logging format change; an EDR exclusion added to reduce false positives may have opened a detection gap; a new workload may have been deployed without the runtime agent. BAS surfaces these failures before adversaries do.

## What BAS does

- **Emulates adversary TTPs** — runs the tactics, techniques, and procedures (TTPs) real attackers use: from initial access and lateral movement to credential theft and data exfiltration. Techniques are executed safely — they demonstrate exploitation capability without causing actual damage.
- **Validates the detection and prevention stack** — does the EDR fire? Does the SIEM generate an alert? Does the WAF block the payload? Does the alert route to the right analyst? BAS answers these questions empirically and continuously.
- **Continuous coverage** — runs on a schedule (daily, weekly) or triggered by changes, catching regressions as environments, configurations, and detection rules change.
- **Maps to MITRE ATT&CK** — frames all results against the [MITRE ATT&CK](https://attack.mitre.org/) matrix so coverage gaps are visible by tactic, technique, and sub-technique.

## BAS, pentest, and purple teaming

| Method | Objective | Frequency | Driven by |
|---|---|---|---|
| Penetration testing | Find vulnerabilities | Annual / quarterly | Human testers |
| BAS | Validate controls detect/prevent known TTPs | Continuous | Automated platform |
| Purple teaming | Improve detection collaboratively | Quarterly / bi-annual | Red + blue together |
| Red teaming | Test detection and response to realistic goal-oriented attack | Annual | Human team |

These are complementary: pentests find new weaknesses, BAS ensures the defenses you rely on keep working between pentests, and purple teaming accelerates detection improvement by having red and blue collaborate rather than operate in opposition.

## The ATT&CK matrix as a coverage map

The MITRE ATT&CK framework organizes adversary behavior into 14 tactics (from Reconnaissance to Impact) and hundreds of techniques. Use it as a coverage map:

1. **Identify priority techniques** — based on threat intelligence relevant to your industry (e.g., financial services organizations face different TTPs than healthcare organizations). Threat reports from CISA, ENISA, and vendor intelligence teams identify which techniques are actively used against your sector.
2. **Run BAS tests** against priority techniques and record: detected, prevented, or neither.
3. **Visualize coverage** using ATT&CK Navigator (a free, web-based tool that color-codes the matrix by coverage status).
4. **Prioritize detection engineering** for undetected but in-use techniques.
5. **Repeat** — rerun after adding new detection rules to verify improvement.

## Closing the loop

BAS value is fully realized only when findings drive action:

- **Undetected technique** → detection engineering task: write or tune a Sigma rule, add a Falco policy, or improve logging to capture the telemetry needed.
- **Detected but unalerted** → SIEM tuning: the event is in the log but no rule fires. Adjust thresholds or add the rule.
- **Alerted but not routed** → response workflow: the alert fires but no one picks it up within SLA. Fix the escalation path.
- **Blocked but not logged** → logging improvement: the control blocked the action but left no audit trail. Add the telemetry.

Without this feedback loop, BAS becomes a metric-reporting exercise rather than a program-improvement engine.

## Purple teaming with BAS tooling

Purple teaming has red and blue operate together, with the red team executing techniques while the blue team watches their SIEM and endpoint consoles in real time. BAS platforms enable this at scale:

1. Red executes an Atomic Red Team test or a BAS platform scenario.
2. Blue confirms detection in the SIEM and assesses alert quality (context, severity, suggested action).
3. Together they tune the detection rule if needed.
4. Test is re-executed to confirm the tuning works.

This collaborative model produces dramatically faster detection improvement than annual red team exercises with a weeks-long reporting gap.

## Running BAS safely

- **Production environments** — run only safe, read-only, or reversible techniques. Simulate the intent (e.g., credential access) without actual credential dumping or data exfiltration.
- **Isolated environments** — run full exploitation chains in a staging environment that mirrors production to test deeper techniques.
- **Change management** — treat BAS runs as scheduled maintenance; notify the blue team so genuine alerts are not confused with simulated ones during non-purple team exercises.
- **Exclude production databases and PII systems** from any write or exfiltration simulations.

## Common pitfalls and anti-patterns

- **BAS as a reporting tool, not a detection-improvement engine** — generating ATT&CK coverage reports that never drive changes to detection rules is theater. Every undetected technique must create a ticket.
- **Running BAS without informing the blue team** — if the SOC investigates a BAS simulation as a real incident, it wastes response capacity. Coordinate schedules.
- **Only testing the EDR** — a comprehensive detection stack includes SIEM, cloud audit logs, network detection, and application logs. BAS coverage should span all telemetry sources.
- **Coverage = detected, not coverage = blocked** — a blocked technique with no detection telemetry is still a gap. You need both prevention and detection.
- **Ignoring persistence and lateral movement techniques** — many BAS programs focus on initial access techniques because they are easy to test. Lateral movement and persistence are where breaches do most of their damage.

## Maturity progression

**Starter** — Deploy Atomic Red Team and run 10–15 high-priority ATT&CK techniques against your endpoint environment. Check SIEM for alerts. Identify gaps. Create detection engineering tickets for undetected techniques.

**Intermediate** — Schedule weekly automated BAS runs across priority techniques. ATT&CK Navigator coverage map reviewed monthly. Purple team session quarterly using BAS findings as the exercise agenda. Detection engineering backlog managed as a first-class project.

**Advanced** — Continuous BAS across all environments (endpoint, cloud, network, application). Full ATT&CK technique coverage tracked as a quarterly KPI. Automated detection-engineering pipeline (BAS finding → Sigma rule proposal → peer review → deployment). BAS results inform threat intelligence prioritization. Annual threat-intelligence-led red team exercises validate detection coverage at the scenario level.

## Metrics and KPIs

- **ATT&CK technique detection rate** — percentage of tested techniques that generated an alert in the SIEM; track by tactic (e.g., lateral movement = 72%, exfiltration = 55%).
- **ATT&CK technique prevention rate** — percentage blocked by preventive controls (EDR, WAF, network policy).
- **Mean time to detect in BAS exercises** — time from technique execution to alert generation; a MTTD proxy using known events.
- **Detection engineering backlog size** — number of open "undetected technique" tasks; should be decreasing or stable.
- **Detection regression rate** — percentage of previously-detected techniques that are no longer detected (control degradation); should be zero between purple team sessions.

---

## Tools[^1]

### Open-source

- [Atomic Red Team](https://github.com/redcanaryco/atomic-red-team) — Library of small, portable, peer-reviewed tests mapped to MITRE ATT&CK; easy to execute individually or automate at scale; the starting point for most BAS programs.
- [Caldera](https://github.com/mitre/caldera) — MITRE's automated adversary emulation platform; supports chained, goal-oriented attack scenarios; C2-like agent for more realistic lateral movement simulation.
- [Infection Monkey](https://github.com/guardicore/monkey) — Open-source breach and attack simulation tool focused on network traversal and lateral movement; good for testing network segmentation controls.
- [Stratus Red Team](https://github.com/DataDog/stratus-red-team) — Cloud-specific BAS: atomic attack techniques for AWS, Azure, GCP, and Kubernetes; fills the gap left by endpoint-focused tools.

### Commercial

- [AttackIQ](https://www.attackiq.com/) — Mature BAS platform with scenario library, ATT&CK coverage analytics, and integrations with major SIEM and EDR platforms; strong enterprise reporting.
- [Cymulate](https://cymulate.com/) — Continuous security validation and BAS across multiple attack surfaces: email, web, endpoint, cloud, lateral movement; good for broad coverage programs.
- [SafeBreach](https://www.safebreach.com/) — BAS across the full kill chain; scenario-based simulations aligned to threat intelligence feeds; strong for financial services and critical infrastructure.
- [Picus Security](https://www.picussecurity.com/) — BAS with a focus on actionable detection and prevention gap analysis; provides ready-made Sigma rules and SIEM queries for detected gaps.

---

### Links

[^1]: Listed in alphabetical order.
