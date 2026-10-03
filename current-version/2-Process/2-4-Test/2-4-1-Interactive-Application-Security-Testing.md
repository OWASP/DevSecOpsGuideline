# Interactive Application Security Testing (IAST)

Interactive Application Security Testing combines the strengths of static and dynamic analysis by **instrumenting the running application** — typically with an agent inside the runtime — and observing it from the inside while it executes. As functional tests, QA, or normal usage exercise the application, the IAST agent watches data flow through the code and reports vulnerabilities with the precise line of code *and* runtime context.

## How IAST differs from SAST and DAST

| Dimension | SAST | DAST | IAST |
|---|---|---|---|
| When it runs | At rest (code/build) | Against running app (black-box) | Inside running app (white-box at runtime) |
| What it sees | Full code, no runtime context | External behavior only | Code paths actually exercised |
| False positive rate | Higher (no runtime proof) | Medium | Very low (confirms real execution) |
| Fix guidance | File + line | HTTP request/response | File + line + full data-flow trace |
| CI integration effort | Low | Medium | Medium (requires test harness) |
| Source code required | Yes | No | No (agent instruments bytecode/binary) |

The combination of inside-view (like SAST) and runtime-view (like DAST) is what makes IAST highly accurate: it only reports a vulnerability when it observes tainted data actually flowing to a dangerous sink in a live execution.

## How it works

An IAST agent is loaded into the application runtime — as a Java agent (`-javaagent`), a .NET profiler, a Node.js hook, or a Python middleware. From there it:

1. **Instruments** method calls, framework hooks, and I/O operations at runtime.
2. **Tracks taint propagation** — marks data coming from user-controlled sources (HTTP params, headers, cookies) and follows it through the call stack.
3. **Alerts on sink contact** — triggers a finding when tainted data reaches a dangerous operation (SQL query, shell execution, file write, deserialization).
4. **Attaches context** — records the exact stack trace, the HTTP request that triggered it, and the source-to-sink path.

Because the agent is passive, it piggybacks on whatever tests are already running — functional tests, integration tests, manual QA — without needing a dedicated attack tool.

## Agent-based vs proxy-based IAST

Some vendors offer a proxy-based variant that sits between the test client and the application (similar to a DAST proxy) while also receiving a lightweight signal from a server-side component. The distinction matters for deployment:

| Approach | How it instruments | Best for |
|---|---|---|
| Agent-based (in-process) | JVM agent, .NET profiler, language hook | Precise taint tracking, low FP, full stack traces; requires supported runtime |
| Proxy-based (network layer) | Intercepts requests/responses; optional server hook | Language-agnostic; less deep taint analysis; easier to deploy in polyglot environments |

Most enterprise IAST tools use the agent-based approach for precision. If your runtime is not supported by an agent, evaluate proxy-based tools or rely on DAST + SAST instead.

## Deploying a Java IAST agent (walkthrough)

Most IAST agents for JVM languages are attached via the standard `-javaagent` JVM flag. Example with Contrast Assess:

```bash
# 1. Download the agent JAR (or include via Maven/Gradle)
curl -L -o contrast.jar https://your-contrast-instance/Contrast/api/ng/contrast.jar

# 2. Set required environment variables
export CONTRAST__API__URL=https://your-contrast-instance/Contrast
export CONTRAST__API__API_KEY=<your-api-key>
export CONTRAST__API__SERVICE_KEY=<your-service-key>
export CONTRAST__API__USER_NAME=<your-username>
export CONTRAST__APPLICATION__NAME=my-app

# 3. Launch the application with the agent attached
java -javaagent:/path/to/contrast.jar \
     -Dcontrast.application.name=my-app \
     -jar myapp.jar

# 4. Run your existing test suite against the instrumented app
mvn verify -Dtest.base.url=http://localhost:8080
```

The agent instruments the JVM bytecode at load time — no source changes required. Findings are reported in real time to the Contrast platform as tests exercise the application.

For CI pipelines, add the `-javaagent` flag to the application startup in your test environment's Dockerfile or Helm values, keeping the agent active for the duration of integration tests.

## Language and framework support

IAST coverage varies by vendor and runtime. Evaluate agents against your stack before committing:

| Runtime | General support level | Notes |
|---|---|---|
| Java / Kotlin (JVM) | Excellent | Most mature; deep framework support (Spring, Struts, Jakarta EE) |
| .NET / .NET Core | Excellent | Good vendor support; profiler API enables deep instrumentation |
| Node.js | Good | Hook-based; coverage varies by framework (Express, Fastify) |
| Python | Moderate | Middleware-based; less deep taint tracking than JVM |
| Go | Limited | No JVM/profiler API; typically proxy-based only |
| Ruby | Limited | Available from some vendors; less mature |

If your primary stack is Go or Ruby, IAST may not deliver the same depth as on JVM/.NET — supplement with strong SAST and DAST coverage.

## Licensing and cost considerations

Most IAST agents are priced per instrumented application instance (per agent process). Costs to model:

- **Per-instance licensing** — if you run IAST in a multi-replica Kubernetes deployment, each pod with the agent counts. For large-scale testing, this adds up.
- **Developer-tier / community editions** — some vendors offer free single-application tiers (e.g., Contrast Community Edition) to evaluate before scaling.
- **Test-only deployment** — containing IAST to test/staging environments (not production) limits licensing cost while still covering meaningful attack surface.

Before selecting a vendor, clarify: per-agent vs per-application pricing, whether replicas count separately, and whether findings from ephemeral environments (PR preview deployments) are included.

## How IAST findings feed vulnerability management

IAST findings should flow into the same vulnerability management pipeline as SAST and DAST:

1. IAST agent reports findings to the vendor platform (or a self-hosted aggregator).
2. Findings are exported via API to [DefectDojo](https://defectdojo.github.io/django-DefectDojo/) or your ASPM platform for deduplication and correlation with SAST/DAST results.
3. New high/critical IAST findings trigger pipeline gates or create tickets in Jira automatically.
4. Developers see a finding with: vulnerable line, HTTP request that triggered it, full taint flow — reducing triage time dramatically.

```bash
# Example: Export IAST findings from Contrast via API
curl -H "API-Key: $CONTRAST_API_KEY" \
     -H "Authorization: $CONTRAST_AUTH" \
     "https://your-contrast/Contrast/api/ng/$ORG_ID/traces/$APP_ID/filter?status=Reported&severity=HIGH,CRITICAL" \
  | jq '.traces[] | {title:.ruleName, severity:.severity, file:.events[-1].stackFrames[0].file}'
```

## Where it fits

Run IAST in QA/test environments alongside automated functional and integration tests, and feed its findings into [Security Gates](../2-3-Build/2-3-5-Security-Gates.md) and the central [vulnerability dashboard](../../3-Governance/3-3-Reporting/3-3-2-Central-vulnerability-management-dashboard.md). Pair it with [DAST](2-4-2-Dynamic-Application-Security-Testing.md) for broader runtime coverage.

A practical pipeline integration:
```
build → deploy to test env (IAST agent active) → run functional/integration tests → IAST findings exported → gate check → promote or block
```

## Common pitfalls and anti-patterns

- **Running IAST against a low-coverage test suite** — results will be sparse and give false confidence. Invest in test coverage first, or add an automated crawler/DAST alongside.
- **Treating IAST as a replacement for SAST** — IAST only covers executed paths; SAST covers the whole codebase. Use both.
- **Ignoring agent version drift** — an outdated agent may miss newly discovered vulnerability classes. Pin agent versions and update on a schedule.
- **Not integrating with the issue tracker** — findings that don't create tickets get lost. Automate the export from IAST to your vulnerability management tool.
- **Running IAST in production** — the performance overhead and potential for finding-triggered alerts in live user sessions make this inadvisable. Confine to test and staging.

## Maturity progression

**Starter** — Deploy one IAST agent on your most critical application in a test environment. Run it during existing integration test runs and review findings manually weekly.

**Intermediate** — Instrument all tier-1 applications. Automate finding export to DefectDojo or Jira. Add a pipeline gate that blocks promotion if new high/critical IAST findings appear.

**Advanced** — Extend to all applications. Correlate IAST findings with SAST and DAST results in an ASPM platform to deduplicate and prioritize. Track IAST coverage as a metric (code paths exercised vs total). Use IAST findings to identify gaps in test suites.

## Metrics and KPIs

- **IAST-verified high/critical findings per release** — should trend downward over time.
- **Mean time to remediate IAST findings** — compare against SAST to assess value of runtime confirmation.
- **Code-path coverage during IAST run** — low coverage indicates test-suite gaps, not application health.
- **False-positive rate** — IAST should be near zero; any FPs indicate misconfiguration of source/sink rules.

---

## Tools[^1]

### Open-source

- [Contrast Community Edition](https://www.contrastsecurity.com/contrast-community-edition) — Free IAST/runtime protection for a single Java or .NET application; good starting point for evaluating agent-based approaches without licensing cost.

### Commercial

- [Checkmarx](https://checkmarx.com/) — Application security platform with interactive testing capabilities; strong if you already use Checkmarx SAST for unified reporting and a single-vendor AppSec suite.
- [Contrast Assess](https://www.contrastsecurity.com/) — Instrumentation-based IAST for multiple runtimes; the most mature agent ecosystem with broad language support and runtime protection (RASP) available on the same agent.
- [HCL AppScan](https://www.hcl-software.com/appscan) — Application security suite including interactive testing; well-suited for enterprises with existing HCL tooling and compliance reporting needs.
- [Seeker (Synopsys)](https://www.synopsys.com/software-integrity/security-testing/interactive-application-security-testing.html) — Strong Java/.NET support with compliance reporting for regulated industries; integrates with Synopsys Black Duck for combined SCA+IAST coverage.

---

### Links

[^1]: Listed in alphabetical order.
