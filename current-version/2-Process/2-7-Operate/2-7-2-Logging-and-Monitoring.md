# Logging and Monitoring

You cannot respond to what you cannot see. Security logging and monitoring provide the visibility needed to detect attacks, investigate incidents, and prove what happened. [OWASP](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/) ranks logging and monitoring *failures* in its Top 10 precisely because so many breaches go undetected for months due to inadequate telemetry. The average time between a breach and its detection has been measured in months — logging is what shortens that window.

## What to log

Capture the events needed to detect and reconstruct security-relevant activity:

- **Authentication and authorization** — logins (success and failure), MFA events, privilege escalations, access denials, token issuance and revocation.
- **Input and validation failures** — malformed requests, schema violations, and application errors that may signal probing or injection attempts.
- **Administrative and configuration changes** — who changed what system configuration, and when.
- **Access to sensitive data and functions** — reads of PII or financial records, use of admin APIs, bulk data exports.
- **Security tooling output** — WAF blocks, IDS/IPS alerts, runtime detection events from Falco, cloud trail events.
- **Session lifecycle** — session creation, expiry, and invalidation.
- **Deployment events** — who deployed what to which environment, from which pipeline run.

Equally important is what *not* to log: never log secrets, passwords, tokens, session cookies, credit card numbers, or unnecessary personal data. Apply privacy-aware logging practices and align with [Data Protection](../../3-Governance/3-2-Data-protection.md). Log categories, not values, for sensitive fields.

## Structured logging

Plain-text logs are difficult to query, correlate, and parse reliably. Adopt structured logging from the start:

```json
{
  "timestamp": "2025-06-27T14:32:11.452Z",
  "level": "WARN",
  "event": "auth.login_failed",
  "user_id": "u-8421",
  "ip": "203.0.113.42",
  "user_agent": "Mozilla/5.0 ...",
  "trace_id": "4bf92f3577b34da6a3ce929d0e0e4736",
  "reason": "invalid_password",
  "attempt_count": 4
}
```

Key practices:
- Consistent event names across services (using a taxonomy like `noun.verb`).
- Correlation IDs (`trace_id`, `request_id`) that flow through the entire request chain for end-to-end reconstruction.
- UTC timestamps with millisecond precision.
- Contextual fields (user, IP, tenant, session) on every security-relevant event.

## Make logs trustworthy

- **Centralize** — aggregate logs from all services, infrastructure, and cloud APIs into a single platform so they can be correlated. Siloed logs cannot detect multi-stage attacks.
- **Tamper-resistant** — write logs to a separate, append-only destination that application credentials cannot modify. An attacker who compromises the app should not be able to erase evidence.
- **Retained sufficiently** — keep logs long enough to investigate slow-burning incidents and meet compliance requirements (PCI DSS requires 12 months; many regulations require at least 6). Hot retention (searchable) for 90 days; cold retention for compliance period.
- **Accurate timestamps** — synchronize clocks across all systems via NTP. A 1-second skew makes incident timelines ambiguous; a 1-minute skew makes them unreliable.
- **Ingestion monitoring** — alert on log gaps (a service that stops logging may have crashed or been tampered with).

## From logging to detection and response

### SIEM and detection-as-code

A SIEM aggregates logs and runs detection rules against them to produce actionable alerts. Modern best practice is **detection-as-code**: write, test, and version-control detection rules exactly like application code.

```yaml
# Example Sigma rule: brute-force login detection
title: Multiple Failed Logins from Same IP
status: stable
logsource:
  category: application
  product: custom-app
detection:
  selection:
    event: auth.login_failed
  timeframe: 5m
  condition: selection | count(user_id) by ip > 10
falsepositives:
  - Automated testing environments
level: high
tags:
  - attack.credential_access
  - attack.t1110
```

[Sigma](https://github.com/SigmaHQ/sigma) is the vendor-neutral format; rules translate to Splunk SPL, Elastic KQL, and other query languages automatically. [RSigma](https://github.com/timescale/rsigma) is an open-source toolkit that lints and tests those rules, evaluates them against log events, and converts them to backend queries.

### MITRE ATT&CK mapping

Map detection rules to [MITRE ATT&CK](https://attack.mitre.org/) technique IDs. This allows you to:
- Visualize coverage gaps on the ATT&CK Navigator.
- Prioritize new detection rules against the most likely attack techniques for your environment.
- Speak a common language with threat intelligence and incident response teams.

### Alerting quality

An alert that nobody can act on is worse than none — it trains the team to ignore alerts. Every alert must:
- Be actionable: the on-call person knows what to do in response.
- Be specific enough to investigate: contains sufficient context (user, IP, affected resource, event sequence).
- Be calibrated: false positive rate below 15% for critical alerts; tune aggressively.
- Link to a runbook that documents the investigation and response procedure.

## Common pitfalls and anti-patterns

- **Logging everything at DEBUG level in production** — creates noise, fills storage, and makes sensitive data harder to redact. Use structured severity levels; log `INFO` for normal events and `WARN`/`ERROR` for anomalies.
- **No log forwarding verification** — teams assume logs are shipping but never verify. Monitor log ingestion volume; alert on drops.
- **Uncontextualized alerts** — an alert that says "login failure detected" with no user, IP, or count is uninvestigatable. Every alert needs context.
- **Treating SIEM as a search engine** — storing logs in a SIEM but only using it to query after an incident is called "detect and do nothing." Invest in proactive detection rules.
- **Clock skew across services** — distributed systems with unsynchronized clocks produce impossible timelines. Enforce NTP for every host.

## Maturity progression

**Starter** — Centralize application and infrastructure logs to a single platform. Ensure authentication events are captured. Set 90-day retention. Create two or three high-value detection rules (brute force, privilege escalation, known-bad IPs).

**Intermediate** — Structured logging with correlation IDs across all services. Detection-as-code with rules in version control. MITRE ATT&CK coverage map. Alert runbooks for every production alert. Tamper-resistant log storage.

**Advanced** — Full observability stack (logs + metrics + traces). Sigma rule library with CI-tested rules. Automated anomaly detection (ML-based baselines). SOAR playbooks for automated first-response. Regular detection coverage reviews using BAS (see [BAS](2-7-6-Breach-and-attack-simulation.md)). Compliance-aligned retention and access control audit trails.

## Metrics and KPIs

- **Mean time to detect (MTTD)** — time from attack start to alert firing; target decreasing over time.
- **Alert-to-incident conversion rate** — percentage of alerts that are real incidents (higher means better tuned detection).
- **False positive rate** — per rule; rules exceeding 15% FP should be revised or suppressed.
- **MITRE ATT&CK coverage** — percentage of relevant techniques with at least one detection rule.
- **Log ingestion gap incidents** — number of times a service stopped shipping logs before it was noticed.

---

## Tools[^1]

### Open-source

- [Grafana + Loki](https://grafana.com/oss/loki/) — Log aggregation and visualization; Loki indexes metadata (labels), not full text, making it cost-efficient at scale; best when paired with the Grafana observability stack.
- [OpenSearch](https://opensearch.org/) — Search, analytics, and log analysis suite (AWS-maintained Elasticsearch fork); strong query capabilities and Dashboards UI; good for teams already using Elasticsearch.
- [Prometheus](https://prometheus.io/) — Metrics-based monitoring and alerting; pair with Grafana for dashboards; does not handle logs (use with Loki for full observability).
- [RSigma](https://github.com/timescale/rsigma) — Sigma detection engineering toolkit; lint, test, and evaluate rules against logs in real time, and convert them to SIEM queries.
- [Sigma](https://github.com/SigmaHQ/sigma) — Open standard for detection rules; write once, compile to any SIEM query language.
- [Wazuh](https://wazuh.com/) — Open-source SIEM with threat detection, file integrity monitoring, vulnerability detection, and compliance dashboards.

### Commercial

- [Datadog](https://www.datadoghq.com/) — Observability and security monitoring platform; unified logs, metrics, traces, and Security Monitoring in one; excellent developer experience.
- [Elastic Security](https://www.elastic.co/security) — SIEM and analytics on the Elastic Stack; large rule library; supports Sigma rule import; strong for teams already invested in the Elastic ecosystem.
- [Splunk](https://www.splunk.com/) — Log analytics and SIEM at scale; mature SPL query language; extensive integration ecosystem; higher cost but industry-standard for large enterprises and regulated industries.

---

### Links

[^1]: Listed in alphabetical order.
