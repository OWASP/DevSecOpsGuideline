# Dynamic Application Security Testing (DAST)

Dynamic Application Security Testing examines a **running application from the outside** — a black-box technique that sends crafted requests and observes responses, exactly as an attacker would. Because it tests the deployed, integrated application, DAST finds vulnerabilities that only appear at runtime: configuration issues, authentication and session flaws, and problems arising from how components interact.

## What DAST finds

- Injection flaws (SQL, command, XSS) observable in responses
- Authentication, session management, and access-control weaknesses
- Security misconfigurations and missing security headers (CSP, HSTS, X-Frame-Options, Permissions-Policy)
- Exposed sensitive data and verbose error handling that leaks stack traces or internal paths
- Server-side issues: SSRF, open redirects, path traversal, insecure deserialization indicators
- Business-logic flaws in multi-step workflows when scans are guided by test scripts

## Strengths and limitations

**Strengths:** language-agnostic (it tests behavior, not code), finds runtime and configuration issues, low false positives for confirmed findings, and reflects the real attacker's view. No source-code access required — works against third-party and compiled applications.

**Limitations:** runs late in the cycle (needs a deployed application), cannot pinpoint the exact vulnerable line of source code, may miss flaws in code paths not reached by the scan, and authenticated/stateful flows require explicit configuration. Scan speed vs. coverage is a constant trade-off.

## Running DAST well

- **Authenticated scans** — configure credentials, session cookies, or OAuth tokens so the scanner reaches protected functionality. A scan that never authenticates only tests the public surface — which may be 10% of the actual attack surface.
- **API-aware testing** — feed the scanner an OpenAPI 3.x, Swagger, or GraphQL introspection schema so it understands modern API surfaces automatically rather than relying on crawling. See [API Security](2-4-4-API-Security.md).
- **Automate in CI/CD** — run against ephemeral test/staging environments on each release candidate. Baseline findings (suppress known accepted issues) to surface only *new* issues per build.
- **Tune scope and rate** — restrict scope to application paths under test; avoid destructive tests (SQLi that drops tables) against shared environments; respect rate limits so you do not DoS your own staging.
- **Use active + passive modes** — passive mode (spider + observe) is safe in shared environments; active mode (attack payloads) should be isolated. Run both in a full pipeline.

## CI/CD integration: OWASP ZAP in GitHub Actions

### Baseline scan (passive — safe for shared envs)

```yaml
# .github/workflows/dast.yml
name: DAST
on:
  push:
    branches: [main]
  pull_request:

jobs:
  zap-baseline:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to ephemeral test environment
        run: |
          # spin up the app (docker-compose, Helm, etc.)
          docker compose -f docker-compose.test.yml up -d
          sleep 10  # wait for health

      - name: OWASP ZAP Baseline Scan
        uses: zaproxy/action-baseline@v0.10.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: '.zap/rules.tsv'   # suppress accepted findings
          fail_action: true
          issue_title: 'DAST Baseline Findings'

      - name: Tear down test environment
        if: always()
        run: docker compose -f docker-compose.test.yml down
```

### Full active scan (release gate)

```yaml
      - name: OWASP ZAP Full Scan (release gate)
        uses: zaproxy/action-full-scan@v0.10.0
        with:
          target: 'http://localhost:8080'
          rules_file_name: '.zap/rules.tsv'
          cmd_options: '-a -j'   # -a: all active rules, -j: report as JSON
          fail_action: true
```

### API scan with OpenAPI spec

```yaml
      - name: OWASP ZAP API Scan
        uses: zaproxy/action-api-scan@v0.6.0
        with:
          target: 'http://localhost:8080/openapi.json'
          format: openapi
          fail_action: true
```

## Handling authenticated flows

For applications behind login, pass credentials or session context to the scanner:

### Token-based auth (JWT / API key)

```yaml
# ZAP replacer rule via environment config
- name: ZAP Authenticated Scan (token)
  uses: zaproxy/action-full-scan@v0.10.0
  with:
    target: 'http://localhost:8080'
    cmd_options: >
      -config replacer.full_list(0).description=auth
      -config replacer.full_list(0).enabled=true
      -config replacer.full_list(0).matchtype=REQ_HEADER
      -config replacer.full_list(0).matchstr=Authorization
      -config replacer.full_list(0).replacement="Bearer ${{ secrets.TEST_JWT }}"
```

### Form-based auth (session cookies)

Use a ZAP authentication script (stored in `.zap/scripts/auth.js`):

```javascript
// ZAP form-based auth script
function authenticate(helper, paramsValues, credentials) {
  var loginUrl = paramsValues.get("Login URL");
  var postData = "username=" + credentials.getParam("Username") +
                 "&password=" + credentials.getParam("Password");
  var msg = helper.prepareMessage();
  msg.setRequestHeader(msg.getRequestHeader().getMethod() + " " + loginUrl + " HTTP/1.1\r\n");
  msg.setRequestBody(postData);
  helper.sendAndReceive(msg);
  return msg;
}
```

### Multi-step flows via HAR replay

Record a browser session as a HAR file and replay it as the scan seed:

```bash
# Replay HAR to seed ZAP's context with a known authenticated session
zap-cli --zap-url http://localhost:8090 spider -c mycontext --start-urls http://app:8080
zap-cli --zap-url http://localhost:8090 import-har /path/to/authenticated-session.har
```

## DAST in ephemeral environments

Modern CI practices spin up a complete application stack per PR (review apps). DAST fits naturally here:

```
PR opened → build image → deploy to ephemeral namespace (k8s) → run DAST → report findings as PR comment → teardown
```

Key considerations for ephemeral DAST:
- **Seed the database** with realistic test data so the scanner reaches meaningful application states
- **Exclude destructive operations** from active scanning in shared environments (configure ZAP's active scan policy to skip SQL mutation tests)
- **Time-box the scan** — a full active scan against a complex app can take 30–60 minutes; use a targeted policy that covers the highest-risk rules in under 10 minutes for PR feedback
- **Teardown on failure** — always destroy the ephemeral environment even if the scan fails (`if: always()` in GitHub Actions)

## False positive management

DAST produces false positives when it misinterprets safe behavior as a vulnerability (e.g., flagging a reflected query parameter as XSS when output is properly encoded). Management strategies:

1. **Rules file (`.zap/rules.tsv`)** — suppress specific rule IDs for paths where the finding is a known false positive:
   ```
   # .zap/rules.tsv format: alert-id  action  url-regex
   10038  IGNORE  .*  # CSP: acceptable in staging
   90033  IGNORE  /health  # info disclosure: health endpoint by design
   ```
2. **Baseline file** — ZAP's `--baseline` mode stores known findings; subsequent runs only fail on *new* issues. Commit the baseline file to source control.
3. **Separate confirmed from informational findings** — gate only on HIGH and MEDIUM confirmed findings; route INFORMATIONAL to a triage queue.
4. **Review the request/response** — for any flagged finding, ZAP records the exact HTTP request that triggered it. Always verify by replaying the request before escalating.

## Integration with defect tracking

Route DAST findings directly to your vulnerability management workflow:

```bash
# Import ZAP JSON report into DefectDojo
curl -X POST "$DEFECTDOJO_URL/api/v2/import-scan/" \
  -H "Authorization: Token $DEFECTDOJO_TOKEN" \
  -F "scan_type=ZAP Scan" \
  -F "file=@zap-report.json" \
  -F "engagement=$ENGAGEMENT_ID" \
  -F "active=true" \
  -F "verified=false"
```

DefectDojo deduplicates against existing findings, maps severity, and creates Jira tickets for new issues automatically if configured. See [Vulnerability Management](../2-7-Operate/2-7-4-Vulnerability-Management.md).

## Where it fits

DAST belongs in the Test stage against a running build, and can also run continuously against staging or production-like environments. Combine it with [IAST](2-4-1-Interactive-Application-Security-Testing.md) (inside view) and [SAST](../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md) (code view) for layered coverage.

## Common pitfalls and anti-patterns

- **Scanning only the homepage** — without authentication or a proper sitemap, DAST covers almost nothing meaningful.
- **Ignoring informational findings** — missing security headers and verbose error messages are exploited in real attacks; do not filter them out entirely.
- **Running active DAST against production** — active scanning sends attack payloads. Always run against isolated test environments; use passive-only scanning if production monitoring is desired.
- **Not baselining known findings** — without a baseline, every run floods the team with the same old issues and the new ones get buried.
- **Skipping API surfaces** — modern applications expose most of their logic through APIs; without an OpenAPI spec feed, DAST will miss the majority of the attack surface.
- **Treating a timed-out scan as a pass** — always check scan completion status, not just exit code.

## Maturity progression

**Starter** — Run OWASP ZAP baseline (passive) scan against a test environment. Review findings manually and create tickets for high/medium. Integrate as a non-blocking CI step.

**Intermediate** — Switch to full active scan against an ephemeral environment per release. Feed OpenAPI spec for API coverage. Baseline known findings and block on *new* high/critical. Export to DefectDojo.

**Advanced** — Authenticated scan covering all user roles. Nuclei templates for business-logic checks. DAST findings correlated with SAST/IAST in ASPM. Continuous passive DAST against staging. Custom scan policies per application risk tier. PR-level ephemeral DAST with findings as PR comments.

## Metrics and KPIs

- **New high/critical findings per release** — primary gate signal; should trend toward zero.
- **Scan coverage (pages/endpoints reached)** — low coverage means the scanner isn't authenticated or the app isn't crawlable.
- **Mean time to remediate DAST findings** — compare by severity tier.
- **False-positive rate** — track confirmed vs total findings; a high FP rate signals the need for better scan configuration.
- **Scan completion rate** — percentage of pipeline runs where DAST completes (vs times out or crashes); low rate indicates infrastructure or configuration issues.

---

## Tools[^1]

### Open-source

- [Darkmoon](https://github.com/ASCIT31/Dark-Moon) — Open-source (GPLv3) autonomous AI penetration-testing CLI that runs black-box, DAST-style assessments against a running application; 50 specialist agents orchestrate 140+ offensive tools over MCP, runs on a local or cloud LLM, and integrates with CI via a GitHub Action and a GitLab CI/CD component.
- [Nikto](https://github.com/sullo/nikto) — Web server scanner for known vulnerabilities and misconfigurations; fast and simple, best for quick server-level checks on infrastructure rather than application logic.
- [Nuclei](https://github.com/projectdiscovery/nuclei) — Fast, template-based vulnerability scanner with a massive community template library; ideal for targeted checks, custom business-logic tests, and CVE-specific validation. Highly scriptable.
- [OWASP ZAP](https://www.zaproxy.org/) — Full-featured web application scanner and intercepting proxy; the most widely used open-source DAST tool with strong CI/CD integrations (GitHub Actions, Jenkins, GitLab CI). Best general-purpose DAST starting point.
- [Wapiti](https://github.com/wapiti-scanner/wapiti) — Black-box web application vulnerability scanner; lightweight alternative to ZAP for scripted environments where a full proxy is not needed.

### Commercial

- [Escape](https://escape.tech/) — DAST focused on APIs and modern web applications; strong GraphQL support and CI-native; best for API-first applications and teams prioritizing developer experience.
- [Invicti (Acunetix/Netsparker)](https://www.invicti.com/) — Automated DAST with proof-based scanning that reduces false positives by confirming exploitability; good for web apps and APIs at scale with compliance reporting.
- [Rapid7 InsightAppSec](https://www.rapid7.com/products/insightappsec/) — Cloud-based DAST with an attack replay feature and integration with the broader Rapid7 platform; best when you already use Rapid7 for vulnerability management.
- [StackHawk](https://www.stackhawk.com/) — Developer-friendly DAST built for CI/CD; runs in Docker with simple YAML configuration; best for developer-owned scanning integrated into GitHub/GitLab workflows.

---

### Links

[^1]: Listed in alphabetical order.
