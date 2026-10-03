# Static Application Security Testing (SAST)

Static Application Security Testing analyzes an application's **source code, bytecode, or binaries without executing it** — a white-box technique that examines the code from the inside. Because it runs early (in the IDE, at pre-commit, and in CI) and needs no running application, SAST is a cornerstone of shift-left security.

## How SAST works mechanically

SAST tools use one or more of these techniques depending on their depth and language support:

- **Pattern matching / AST analysis** — the simplest and fastest approach. The tool parses source code into an Abstract Syntax Tree (AST) and matches against known-vulnerable patterns (e.g., "string concatenation used as SQL query argument"). Semgrep and Bandit use this approach. Fast, low false-positive rate, but misses vulnerabilities that span multiple functions.
- **Dataflow / taint analysis** — the most powerful technique. The tool tracks how untrusted input (a *source*, such as `request.getParameter()`) flows through the application until it reaches a dangerous operation (a *sink*, such as `executeQuery()`). If tainted data reaches a sink without sanitization, it is flagged. CodeQL and Checkmarx use this approach. More thorough, higher false-positive rate, slower.
- **Control flow analysis** — maps all possible execution paths through a function or module to find paths that lead to dangerous states (e.g., null dereference, unhandled exception disclosing information).
- **Semantic analysis** — understands language idioms and framework conventions rather than just syntax, reducing false positives for framework-specific patterns.

The practical implication: faster pattern-matching tools are suitable for IDE and pre-commit; deeper dataflow tools belong in nightly CI scans.

## What SAST finds

By tracing data and control flow through the code, SAST detects flaws such as:

- Injection (SQL, command, LDAP) from untrusted input reaching dangerous sinks
- Cross-site scripting (XSS) and unsafe output handling
- Hardcoded secrets and weak cryptography
- Insecure deserialization and path traversal
- Coding-standard and error-handling violations that lead to security bugs

## Strengths and limitations

**Strengths:** runs without a deployed app, finds issues at the earliest stage, points directly to the vulnerable line, and covers code paths that dynamic testing might never reach.

**Limitations:** SAST cannot see runtime or environment context — it produces **false positives** (flagging safe code as vulnerable) and can miss flaws that only appear at runtime (logic bugs, auth issues that depend on data state). The key to a healthy SAST program is managing noise.

## The SAST tuning process

A SAST program that is not actively tuned will degrade. Teams learn to ignore alerts, and real findings get buried. Follow this cycle:

1. **Establish baseline** — run the tool in report-only mode for 2–4 weeks. Record all findings. This is the debt you already own; do not gate on it immediately.
2. **Review a sample** — triage 50–100 random findings manually. Measure: what fraction are genuine vulnerabilities? What fraction are false positives? Which rule categories produce the most noise?
3. **Suppress high-noise rules** — rules with > 80% false positive rate for your codebase should be disabled or scoped. Document the suppression with justification.
4. **Gate on new findings only** — using the baseline snapshot, block pull requests only on findings that are *new* since the baseline. This removes legacy debt from the gate and makes it actionable.
5. **Reduce the baseline progressively** — allocate sprint capacity to address the existing backlog. Track baseline count month-over-month.
6. **Re-tune quarterly** — as the codebase and frameworks evolve, repeat the sample review to catch new noise sources.

## SAST scan modes: when to use each

| Mode | Tool | Scope | Latency | Purpose |
|---|---|---|---|---|
| IDE plugin | Semgrep LSP, Snyk Code, SonarLint | File being edited | < 1 second | Instant feedback; education at code time |
| Pre-commit | Semgrep (fast rules) | Changed files only | 5–30 seconds | Catch obvious issues before push |
| Pull request | Semgrep, CodeQL, Snyk Code | Diff vs base branch | 1–5 minutes | Authoritative gate; block on new high/critical |
| Nightly full scan | CodeQL, Checkmarx, Fortify | Entire codebase | 10–60 minutes | Deep taint analysis; feed central dashboard |

## Integrating SAST in the pipeline

```yaml
# Example GitHub Actions SAST step using CodeQL
- name: Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: javascript, python
    queries: security-extended

- name: Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v3
  with:
    category: "/language:javascript"
```

## Writing a custom Semgrep rule

For organization-specific patterns — internal APIs that must always be called with authentication, deprecated functions that must not be used — write custom rules:

```yaml
# rules/no-unsafe-internal-api.yaml
rules:
  - id: no-unauthenticated-internal-client
    patterns:
      - pattern: InternalClient($HOST, ...)
      - pattern-not: InternalClient($HOST, auth=$AUTH, ...)
    message: |
      InternalClient must always be called with an explicit auth= parameter.
      Unauthenticated calls will be rejected in production.
    languages: [python]
    severity: ERROR
    metadata:
      category: security
      cwe: "CWE-306: Missing Authentication for Critical Function"
```

Run: `semgrep --config rules/ src/`

Custom rules are the primary mechanism for catching organization-specific security patterns that generic rulesets cannot know about.

## SAST for infrastructure code

SAST is not only for application code. The same principles apply to infrastructure:

- **Terraform / Bicep / CloudFormation** — see [IaC Scanning](../2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md) for dedicated tooling.
- **GitHub Actions / GitLab CI / CircleCI** — pipeline definitions can contain command injection, secret exposure, and unsafe permission grants. Tools like `zizmor` (GitHub Actions) and `checkov` analyze CI pipeline files statically.
- **Dockerfiles** — running as root, `ADD` instead of `COPY`, pinning base images to digests.

Covering infrastructure-as-code alongside application code gives a complete static security picture.

## SAST and ASPM integration

Raw SAST output fed directly to developers produces too much noise. At scale, route SAST findings through an [ASPM](../../../3-Governance/3-3-Reporting/3-3-3-ASPM.md) or central platform (DefectDojo, Dependency-Track) that:

- **Deduplicates** — the same vulnerability found by CodeQL, Semgrep, and Snyk Code is one finding, not three.
- **Enriches** — adds reachability context, EPSS scores, and business asset classification.
- **Assigns ownership** — maps findings to the team that owns the affected service.
- **Tracks SLAs** — monitors time-to-remediate by severity against agreed targets.

This prevents each tool's dashboard from becoming a siloed, ignored alert queue.

## Common pitfalls and anti-patterns

- **Scanning everything, gating nothing** — running SAST but not blocking on results means findings are ignored. Combine scanning with actionable gates.
- **Default rules on unfamiliar languages** — out-of-the-box rules for a language or framework you do not use inflate false positives. Scope rules to your actual stack.
- **Ignoring baseline debt** — gating on total findings punishes teams for historical debt. Gate on *new* issues introduced since a known-good baseline.
- **Single pipeline stage only** — skipping IDE/pre-commit integration means developers first see findings only after a full CI run, slowing feedback loops significantly.
- **No triage ownership** — findings with no assigned owner go unresolved. Every finding needs a team responsible for the remediation or exception decision.
- **Suppressing via inline comments without tracking** — `# nosec`, `// NOSONAR`, and similar inline suppressions are invisible in most dashboards. Route suppressions through a central exception register.

## Maturity progression

**Starter** — Run Semgrep or Bandit in CI with a default ruleset. Report findings; do not block yet. Build developer familiarity with the tool and its output.

**Intermediate** — Gate pull requests on new high/critical findings vs. a baselined snapshot. Integrate IDE plugins (SonarLint, Snyk Code). Tune false-positive-heavy rules. Route findings to a central tracker (DefectDojo). Write 2–3 custom rules for internal anti-patterns.

**Advanced** — Use semantic/dataflow tools (CodeQL, Checkmarx) for deep taint analysis. Enable AI-assisted triage and autofix suggestions. Feed findings enriched with reachability and EPSS into ASPM. Track escape rate (issues reaching production) and MTTR by severity. Custom rules cover all critical internal security patterns.

## Metrics and KPIs

| Metric | Target |
|---|---|
| False positive rate | < 20% of findings after tuning |
| Mean time to remediate (critical) | < 7 days |
| New high/critical findings per release | Trending toward zero |
| Escape rate (issues found post-merge) | Decreasing quarter-over-quarter |
| Developer satisfaction with SAST tooling | > 70% positive in surveys |
| Rules suppressed with documented justification | 100% (zero undocumented suppressions) |

---

## Tools[^1]

### Open-source

- [Bandit](https://github.com/PyCQA/bandit) — Security-focused static analysis for Python. Best for Python-only codebases; fast, easy to extend with custom plugins. Limited to pattern matching; no dataflow.
- [Brakeman](https://github.com/presidentbeef/brakeman) — Static analysis scanner for Ruby on Rails. Deep Rails-specific knowledge makes it highly accurate for that stack; not applicable outside Rails.
- [CodeQL](https://github.com/github/codeql) — Semantic code analysis engine treating code as data for cross-codebase vulnerability queries. Strong for Java, C/C++, JavaScript, Python; integrated free in GitHub Advanced Security. Deep dataflow; slower but thorough.
- [gosec](https://github.com/securego/gosec) — Security analyzer for Go source code; maps findings to CWE and G-codes; ideal for Go microservices.
- [Semgrep](https://semgrep.dev/) — Fast, multi-language pattern-based static analysis with a large community rule registry. Low barrier to writing custom rules; best-in-class for IDE integration and speed. No native dataflow analysis (available in Semgrep Pro).
- [SonarQube Community](https://www.sonarsource.com/products/sonarqube/) — Web-based static analysis across 20+ languages with quality gate integration; broad language coverage for polyglot teams.

### Commercial

- [Checkmarx SAST](https://checkmarx.com/) — Enterprise SAST with deep dataflow analysis and broad language support; strong for regulated industries. Full taint analysis across the full application graph.
- [Fortify Static Code Analyzer](https://www.opentext.com/products/fortify-static-code-analyzer) — Long-established enterprise SAST with binary analysis; commonly required in government and defense contexts.
- [Snyk Code](https://snyk.io/product/snyk-code/) — Developer-first SAST with real-time IDE feedback and AI-suggested fixes; fastest time-to-value for developer adoption. Strong on JavaScript/TypeScript and Python.
- [Veracode Static Analysis](https://www.veracode.com/products/binary-static-analysis-sast) — SaaS SAST with binary scanning; no source-code access required, useful for third-party assessments and vendor security reviews.

---

### Links

[^1]: Listed in alphabetical order.
