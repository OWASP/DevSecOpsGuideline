# Linting Code

Linting analyzes source code for stylistic issues, bugs, and suspicious patterns without running it. While linters started as style and quality tools, modern linters and their security plugins catch a meaningful share of security problems — making linting a fast, low-friction first line of defense that fits naturally in pre-commit and CI.

## Why linting matters for security

- **Consistency reduces risk** — consistent, readable code is easier to review and less likely to hide bugs in unexpected places.
- **Security rules catch real flaws** — many linters detect dangerous functions, injection-prone patterns, weak crypto usage, insecure randomness, and hardcoded values.
- **Fast feedback** — linters run in seconds on a developer's machine, so they belong at pre-commit and on every pull request without meaningfully slowing the pipeline.
- **Bridge to SAST** — lightweight, rule-based scanners like Semgrep blur the line between linting and [SAST](../../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md), giving security depth at lint speed.

## Where to run it

Run linting at every layer for maximum coverage without introducing bottlenecks:

- **IDE** — real-time feedback as the developer types. This is the lowest-friction catch — the developer sees the issue at the moment of creation. IDE plugins for ESLint, Bandit, Semgrep, and language servers can highlight problems inline.
- **Pre-commit** — block obvious issues before they enter history. Scope checks to changed files only (using `lint-staged` or Lefthook's `glob` filtering) to keep execution fast. See [Pre-commit](2-2-1-1-Pre-commit.md).
- **CI** — authoritative enforcement that cannot be bypassed. Fail the build on new violations. Run the full rule set here, not just the fast subset used at pre-commit.

## Scope to lint

### Application code

Enable security rule sets in language-specific linters. Do not run only style rules — security rules are where the risk is:

| Language | Linter | Security rules |
|---|---|---|
| Python | Bandit, Semgrep, Ruff | B-prefix rules (Bandit); `S` rules (Ruff, flake8-bandit port); `p/python` rule set (Semgrep) |
| JavaScript / TypeScript | ESLint + `eslint-plugin-security`, Semgrep | `no-eval`, `no-new-func`, XSS patterns, `detect-non-literal-regexp` |
| Go | golangci-lint (includes gosec) | gosec rules (G1xx–G7xx, see the [gosec rule list](https://github.com/securego/gosec/blob/master/RULES.md)) |
| Java | SpotBugs + find-sec-bugs, Semgrep | `find-sec-bugs` plugin detects SQL injection, XXE, SSRF |
| Ruby | Brakeman | Full Rails-aware security analysis |
| PHP | Psalm, Semgrep | Psalm taint analysis (`--taint-analysis`); `p/php` rule set (Semgrep) |
| Kotlin / Android | Android Lint, Detekt, Semgrep, SpotBugs + find-sec-bugs | Android Lint security checks; Semgrep Kotlin/Android rule sets; find-sec-bugs works on Kotlin bytecode |

### Infrastructure as code

Lint IaC files for misconfiguration:

- **Dockerfile** — `hadolint` enforces best practices: no `latest` tag, `USER` instruction set, shell injection in `RUN` commands.
- **Terraform** — `tflint` for correctness and provider-specific errors, and `Trivy` (`trivy config`) for security misconfigurations before `terraform apply`. `tfsec` has been folded into Trivy and is no longer actively developed.
- **Kubernetes manifests** — `kube-linter` checks for privilege escalation, missing resource limits, host network access.
- **Helm charts** — `helm lint` + `kube-linter` on rendered templates.

See [IaC Scanning](../../2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md) for deeper coverage.

### Configuration and data files

Validate YAML/JSON/TOML in CI to prevent malformed or unsafe config from reaching deployment:

```yaml
# .pre-commit-config.yaml entry
- repo: https://github.com/pre-commit/pre-commit-hooks
  rev: v6.0.0
  hooks:
    - id: check-yaml
    - id: check-json
    - id: check-toml
```

## Practical Semgrep example

Semgrep lets you write custom rules in YAML to enforce project-specific security patterns:

```yaml
# semgrep-rules/no-md5.yaml
rules:
  - id: no-md5-for-hashing
    patterns:
      - pattern: hashlib.md5(...)
    message: "MD5 is cryptographically broken. Use hashlib.sha256() or better."
    languages: [python]
    severity: ERROR
    metadata:
      category: security
      cwe: CWE-327
```

Run it in CI:

```bash
semgrep --config semgrep-rules/ --error --json > semgrep-results.json
```

## Baseline management

New projects inherit years of existing lint violations. Blocking on all of them at once is counterproductive. Manage this with baselines:

- **Semgrep baseline** — `semgrep --baseline-commit <sha>` reports only findings introduced after the baseline commit, not the historical backlog.
- **ESLint** — use bulk suppressions (`eslint --suppress-all`, ESLint v9.24+) to record existing violations in `eslint-suppressions.json`, then fail only on new ones and clear the backlog incrementally. `--report-unused-disable-directives` helps keep inline suppressions honest.
- **detect-secrets baseline** — generate a baseline file with `detect-secrets scan > .secrets.baseline` and commit it. New secrets are flagged against the baseline.

Treat clearing lint debt as technical debt: schedule it, track it, and do not let it grow by blocking new violations.

## Common pitfalls

- **Security rules disabled** — style linting without security rules enabled misses the most valuable signal. Audit your `eslint.config.js` (or legacy `.eslintrc`) / `pyproject.toml` to confirm security plugins are active.
- **Noisy rules driving suppression** — if developers add `# noqa`, `// eslint-disable`, or `// nosec` comments routinely, the rules are misconfigured. Tune or replace noisy rules instead of suppressing them everywhere.
- **Only running in CI, not at pre-commit** — slow feedback loops mean developers context-switch after forgetting what the code was doing.
- **Linting only changed files in CI** — fine for speed, but run full-repo linting on a schedule (weekly) to catch violations in unchanged files.
- **Ignoring `lint-staged` performance** — on large repos, running linters against all files at pre-commit is slow. Scope to staged files.

## Metrics

- Number of security-category lint violations introduced per sprint (should trend toward zero).
- `# noqa` / `// eslint-disable` suppression count per repo (rising counts indicate noise problems or avoidance).
- Time from lint violation to fix (measures how actionable feedback is).
- Percentage of repos with security lint rules enabled (org-level metric).

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Style linter running in CI; security rules added to at least one language linter |
| Developing | Security linting (Semgrep or equivalent) at pre-commit and CI; IaC linting for Dockerfile and Terraform; baseline managed |
| Defined | Custom Semgrep rules for project-specific patterns; IDE plugins standard in developer tooling; violations trend tracked |
| Advanced | Org-wide shared Semgrep rule library; lint results fed into ASPM for correlation with runtime findings; suppressions reviewed in security audits |

---

## Tools[^1]

### Open-source

- [Bandit](https://github.com/PyCQA/bandit) — Finds common security issues in Python code. Checks for dangerous calls (`exec`, `eval`, `pickle`), weak crypto, SQL injection patterns, and more. Integrates with pre-commit and CI.
- [Brakeman](https://brakemanscanner.org/) — Static analysis specifically for Ruby on Rails. Detects SQL injection, XSS, mass assignment, and other Rails-specific security issues.
- [ESLint](https://eslint.org/) — Pluggable JavaScript/TypeScript linter. Add `eslint-plugin-security` and `eslint-plugin-no-unsanitized` for security rules covering `eval`, regular expression injection, and unsafe HTML insertion.
- [golangci-lint](https://golangci-lint.run/) — Fast aggregator of Go linters. Includes `gosec` for security analysis (hardcoded credentials, SQL injection, weak crypto, file permissions).
- [hadolint](https://github.com/hadolint/hadolint) — Dockerfile linter that enforces best practices: avoid `latest` tags, set non-root `USER`, avoid shell injection in `RUN`.
- [kube-linter](https://github.com/stackrox/kube-linter) — Static checks for Kubernetes manifests and Helm charts: privileged containers, missing resource limits, host namespace access, and more.
- [Opengrep](https://github.com/opengrep/opengrep) — Community fork of Semgrep CE (LGPL 2.1, backed by a consortium of AppSec vendors) that remains compatible with Semgrep rules. Consider it if you need open-source features, such as intrafile taint analysis, that Semgrep keeps in its commercial tier.
- [Ruff](https://docs.astral.sh/ruff/) — Very fast Python linter and formatter. Its `S` rules reimplement many Bandit checks, so one tool can cover style and basic security at pre-commit speed.
- [Semgrep](https://semgrep.dev/) — Fast, multi-language static analysis using readable YAML pattern rules. Community registry contains thousands of security rules. Supports custom rules for project-specific patterns. The Community Edition engine is open source; some cross-file analysis and the managed rule packs require the commercial platform.
- [ShellCheck](https://www.shellcheck.net/) — Static analysis for shell scripts: unquoted variables, command injection patterns, and portability bugs. Useful for CI scripts and Dockerfile `RUN` helpers.
- [SpotBugs + find-sec-bugs](https://find-sec-bugs.github.io/) — SpotBugs is a Java bytecode analyzer; find-sec-bugs adds 130+ security bug patterns covering OWASP Top 10 for Java/Kotlin.
- [TFLint](https://github.com/terraform-linters/tflint) — Terraform linter that catches invalid provider arguments, deprecated syntax, and module issues. Pair it with Trivy for security checks.

### Commercial

- [SonarQube Server / SonarQube Cloud](https://www.sonarsource.com/products/sonarqube/) — Code quality and security analysis across 30+ languages (formerly SonarQube and SonarCloud). The open-source Community Build is free; commercial editions add deeper security analysis, security hotspot management, portfolio reporting, and branch analysis.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [Semgrep rule registry](https://semgrep.dev/r)
- [gosec — Go security checker](https://github.com/securego/gosec)
- [OWASP Cheat Sheet — Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Injection_Prevention_Cheat_Sheet.html)
