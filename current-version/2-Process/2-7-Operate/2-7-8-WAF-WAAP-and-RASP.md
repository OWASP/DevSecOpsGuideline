# Runtime Application Protection: WAF, WAAP, and RASP

Secure development reduces vulnerabilities, but production applications will still contain flaws that are unknown, unpatched, or not yet fixable. **Runtime application protection** adds compensating controls in front of or inside the application to block exploitation while engineering remediates. It is a safety net, not a substitute for fixing the root cause found by [SAST](../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md), [DAST](../2-4-Test/2-4-2-Dynamic-Application-Security-Testing.md), and [API security testing](../2-4-Test/2-4-4-API-Security.md).

## The control landscape

| Control | Where it runs | What it sees | Strengths | Limits |
|---|---|---|---|---|
| **WAF** (Web Application Firewall) | Reverse proxy, CDN, ingress, or load balancer | HTTP requests and responses | Fast to deploy, protects legacy and third-party apps, no code change | Blind to application context; bypassable by encoding and logic abuse; false positives |
| **WAAP** (Web Application and API Protection) | Typically cloud/edge platform | WAF plus API, bot, and DDoS signals | Combines WAF, API discovery and schema enforcement, bot management, and L7 DDoS | Platform dependency; depends heavily on tuning and API inventory |
| **RASP** (Runtime Application Self-Protection) | Inside the application process via agent or library | Execution context: the SQL query, file path, or command actually being run | Low false positives for injection classes; sees decrypted, post-parsing data | Per-language agents, performance and stability cost, deployment effort |

These layer rather than compete: a WAF/WAAP reduces noise and handles volumetric and known-bad traffic; RASP confirms exploitation inside the app where the WAF cannot be sure.

## WAF and WAAP in practice

### Rules and the OWASP Core Rule Set

The [OWASP Core Rule Set (CRS)](https://coreruleset.org/) is a generic attack-detection rule set for ModSecurity-compatible engines, covering injection, XSS, and protocol abuse. CRS uses **anomaly scoring**: rules add to a per-request score and the request is blocked only when a threshold is reached, which makes tuning predictable. Key knobs are the **paranoia level** (higher = more rules, more false positives) and the **anomaly thresholds**.

Roll out in detection mode first, using ModSecurity-compatible SecLang (also supported by Coraza):

```apache
# Phase 1: observe only
SecRuleEngine DetectionOnly
SecAuditEngine RelevantOnly
SecAuditLog /var/log/modsec_audit.log

# Phase 2: enforce, with CRS anomaly thresholds (CRS defaults shown)
SecRuleEngine On
SecAction "id:900110,phase:1,pass,nolog,\
  setvar:tx.inbound_anomaly_score_threshold=5,\
  setvar:tx.outbound_anomaly_score_threshold=4"
```

Check the CRS documentation for the exact configuration of your engine and CRS version. Engine options include [ModSecurity](https://github.com/owasp-modsecurity/ModSecurity) (now an OWASP project) and [Coraza](https://coraza.io/), a Go engine compatible with SecLang and CRS v4 that embeds in proxies such as Caddy and Envoy, among others.

### Tuning, not disabling

False positives are the main reason WAFs are left in log-only mode forever. Handle them narrowly:

```apache
# Exclude one parameter from one rule instead of disabling the rule globally
SecRuleUpdateTargetById 942100 "!ARGS:comment"
# Scope an exclusion to a single path
SecRule REQUEST_URI "@beginsWith /admin/editor" \
  "id:1001,phase:1,pass,nolog,ctl:ruleRemoveById=941100"
```

Review blocked and would-have-blocked requests regularly with the application team, keep exclusions in version control, and re-test after application releases.

### Virtual patching

When a vulnerability is known but the fix will take time, deploy a narrow rule that blocks the specific exploit pattern at the edge while the code fix is prepared:

```apache
# Temporary: block exploitation of CVE-XXXX-YYYY in the 'id' parameter of /api/export
SecRule REQUEST_URI "@beginsWith /api/export" \
  "id:1900001,phase:2,deny,status:403,log,msg:'Virtual patch for CVE-XXXX-YYYY',\
  chain"
  SecRule ARGS:id "!@rx ^[0-9]{1,10}$"
```

Treat virtual patches as temporary: link each to a ticket and CVE, test that they block a known exploit and permit normal traffic, and remove them once the fix ships. Feed vulnerability intake from [Vulnerability Management](2-7-4-Vulnerability-Management.md).

### API protection and bot defense

- **API protection** — import the OpenAPI schema and enforce it (allowed paths, methods, parameter types, content types, body size). Use API discovery to find undocumented "shadow" endpoints. WAF signatures do not stop broken object-level authorization or business-logic abuse; those need application-level fixes (see [API Security](../2-4-Test/2-4-4-API-Security.md)).
- **Rate limiting and abuse controls** — limit by client, token, and endpoint, with stricter limits on authentication, password reset, and costly operations.
- **Bot defense** — distinguish credential stuffing, scraping, and carding from legitimate automation using behavior, reputation, and challenge mechanisms. Be aware that determined bots evade simple IP and user-agent rules, and that challenges affect accessibility and user experience.

## RASP in practice

RASP instruments the runtime (for example through a Java agent or language library) to observe and block dangerous operations in context: a SQL statement whose structure was altered by user input, a file access outside an allowed directory, or an unexpected process spawn. Adopt it where injection risk is high and code changes are slow, and:

- Start in monitor mode and compare its findings with WAF logs and DAST results.
- Measure latency and memory overhead under load testing before enabling blocking.
- Plan for agent upgrades alongside runtime and framework upgrades.

IAST agents and RASP agents are often the same technology in different modes; see [IAST](../2-4-Test/2-4-1-Interactive-Application-Security-Testing.md).

## Common pitfalls and anti-patterns

- **WAF left in detection-only forever** — it generates logs, not protection. Set a date and criteria for moving to blocking.
- **Blocking with no tuning** — switching to block mode on day one at a high paranoia level breaks legitimate traffic and gets the WAF disabled.
- **Origin reachable directly** — attackers bypass a cloud WAF/CDN by hitting the origin IP. Restrict origin access to the WAF's addresses or use authenticated origin pulls/mTLS.
- **WAF as the fix** — a virtual patch or signature is a stopgap; the underlying flaw remains and is often bypassable.
- **Ignoring TLS and request-body limits** — traffic the WAF cannot decrypt, parse, or inspect (oversized bodies, unusual encodings) passes uninspected.
- **No one owns the alerts** — blocked-request logs must reach the SIEM and be reviewed (see [Logging and Monitoring](2-7-2-Logging-and-Monitoring.md)).
- **Treating bots as a WAF problem** — business-logic abuse needs rate, identity, and fraud controls beyond signatures.

## Maturity progression

**Starter** — WAF or managed edge protection in front of internet-facing apps with CRS in detection mode. Logs shipped to the SIEM. Origin access restricted to the WAF.

**Intermediate** — Blocking mode for the most reliable rule categories, with documented exclusions in version control and a regular false-positive review. OpenAPI-based schema validation and rate limits for APIs. Virtual patching process tied to vulnerability management.

**Advanced** — Full blocking with CRS tuned per application, WAF rules tested in CI/CD against regression and attack traffic, API discovery for shadow endpoints, bot management for authentication and checkout flows, and RASP for high-risk applications. WAF/RASP telemetry correlated with DAST, pentest, and incident data to drive fixes.

## Metrics and KPIs

- **Percentage of internet-facing apps/APIs behind a WAF/WAAP in blocking mode.**
- **False-positive rate** — legitimate requests blocked, from support tickets and review.
- **Virtual patch age** — time each virtual patch has been in place before the code fix; target is days, not months.
- **Blocked attacks by category** — trends in injection, scanner, and bot traffic.
- **Detection-to-block conversion time** — how long new apps spend in detection-only mode.
- **Origin exposure** — number of apps whose origin accepts traffic not coming from the WAF.

---

## Tools[^1]

### Open-source

- [BunkerWeb](https://github.com/bunkerity/bunkerweb) — NGINX-based open-source WAF with ModSecurity and CRS integration (AGPL-3.0).
- [Coraza](https://coraza.io/) — OWASP Go WAF engine compatible with SecLang and the Core Rule Set; embeds in proxies and runs as a library.
- [ModSecurity](https://github.com/owasp-modsecurity/ModSecurity) — The long-standing open-source WAF engine, now maintained under OWASP, with v2 (Apache) and v3 (NGINX and others) lines.
- [NAXSI](https://github.com/wargio/naxsi) — Allow-list-style NGINX WAF module with low rule maintenance (GPL-3.0); the original nbs-system repository was archived and this fork continues it.
- [OWASP Core Rule Set](https://github.com/coreruleset/coreruleset) — Generic attack-detection rules for ModSecurity-compatible engines.
- [open-appsec](https://github.com/openappsec/openappsec) — Machine-learning-based WAF/API protection engine for NGINX, Kong, and Kubernetes ingress (Apache 2.0; the advanced ML model has its own license).

### Commercial

- [Akamai App & API Protector](https://www.akamai.com/products/app-and-api-protector) — Edge WAAP with API discovery, bot management, and DDoS protection.
- [AWS WAF](https://aws.amazon.com/waf/) — Managed WAF for CloudFront, ALB, and API Gateway with managed rule groups and bot control.
- [Cloudflare WAF](https://www.cloudflare.com/application-services/products/waf/) — Edge WAF with managed rules, API Shield, and bot management.
- [Contrast Protect](https://www.contrastsecurity.com/) — Agent-based RASP built on the same instrumentation as Contrast's IAST.
- [F5 Distributed Cloud WAAP](https://www.f5.com/cloud/products/web-app-and-api-protection) — WAAP across multi-cloud and edge, including bot and API protection.
- [Imperva](https://www.imperva.com/) — WAF, API security, bot management, and RASP.

---

### Links

- [OWASP Core Rule Set documentation](https://coreruleset.org/docs/)
- [OWASP Coraza](https://coraza.io/)
- [OWASP Automated Threats to Web Applications](https://owasp.org/www-project-automated-threats-to-web-applications/)

[^1]: Listed in alphabetical order.
