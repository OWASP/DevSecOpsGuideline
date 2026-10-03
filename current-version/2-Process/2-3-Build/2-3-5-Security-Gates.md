# Security Gates

A **security gate** is a checkpoint in the pipeline that decides whether code or an artifact is allowed to proceed — to merge, to be released, or to be deployed — based on security criteria. Gates are how shift-left scanning translates into actual risk reduction: a finding that never blocks anything rarely gets fixed.

The idea is simple: catch problems before they hit production. A vulnerability found during a pull request costs minutes to fix. The same vulnerability found in production is an incident, potentially a breach, and weeks of cleanup.

The hard part is not adding gates; it is designing gates that reduce risk **without destroying developer flow**. Gates that are too noisy or too strict get disabled, ignored, or bypassed.

## Principles for effective gates

- **Gate on risk, not raw counts** — block on severity, exploitability, and reachability, not on the total number of findings. A gate that blocks on "any medium CVE in any transitive dependency" will be overridden within a week.
- **Baseline existing issues** — hold teams accountable for *new* risk they introduce, not the entire backlog of legacy debt at once. Use a known-good baseline snapshot and block only on findings that did not exist in the baseline.
- **Fail fast and clearly** — when a gate blocks, tell the developer exactly what, where, and how to fix it. A gate that says "build failed" with no guidance is friction without value.
- **Provide a path forward** — support documented, time-boxed risk acceptance / exceptions with an owner, rather than forcing developers to silently disable checks.
- **Tune relentlessly** — high false-positive rates are the fastest way to lose developer trust; treat noise as a bug in the gate, not a developer compliance problem.

## Where to place gates

```text
+-----------------------------------------------------------------------------+
|                        CI/CD Pipeline Security Gates                         |
+-------------+-------------+-------------+-------------+---------------------+
|  Pre-Commit |    Build    |    Test     |   Release   |       Deploy        |
+-------------+-------------+-------------+-------------+---------------------+
| - Secrets   | - SAST      | - DAST      | - Image     | - Admission         |
|   scanning  | - SCA       | - IAST      |   signing   |   controllers       |
| - Linting   | - Container | - Pentest   | - SBOM      | - Runtime           |
| - Hooks     |   scanning  |   (staged)  |   generation|   policies          |
|             | - IaC scan  |             | - Artifact  | - Network           |
|             |             |             |   attestation|  policies          |
+-------------+-------------+-------------+-------------+---------------------+
```

| Stage | Typical gate | Failure mode |
| --- | --- | --- |
| Pre-commit / IDE | Secrets, linting, fast SAST (advisory) | Advisory only — educate, don't block here |
| Pull request | SAST, SCA, IaC — block new high/critical | Block merge; surface in PR comment with fix guidance |
| Build | Full scans, container scan, SBOM generation | Block artifact promotion from build stage |
| Release | Signed artifacts, provenance, no unresolved criticals | Block publishing to production registry |
| Deploy | Admission control: only signed, policy-compliant artifacts | Block workload from running in cluster |

```yaml
# Example: GitHub Actions gate using Semgrep — blocks on new high findings
- name: Semgrep SAST gate
  uses: returntocorp/semgrep-action@v1
  with:
    config: >
      p/owasp-top-ten
      p/secrets
    publishToken: ${{ secrets.SEMGREP_APP_TOKEN }}
  env:
    SEMGREP_BASELINE_REF: ${{ github.base_ref }}  # diff-aware: new findings only
```

## Defining thresholds and policy

### Decide what blocks before wiring up tools

Before adding scanners, decide what blocks a deployment versus what only logs a warning. A common starting point:

| Severity | Action | Example threshold |
|----------|--------|-------------------|
| Critical | Block deployment | 0 allowed |
| High | Block deployment | 0 allowed |
| Medium | Warn, require approval | 5 or fewer allowed |
| Low | Warn only | No limit (track) |

### Centralize gate policy

Keep gate policies in a single, version-controlled config so every team knows exactly what is enforced:

```yaml
# .security-gates.yaml
version: "1.0"
gates:
  sast:
    enabled: true
    fail_on:
      critical: true
      high: true
      medium: false
    tools:
      - semgrep
      - codeql

  sca:
    enabled: true
    fail_on:
      critical: true
      high: true
    max_age_days: 30  # Fail if dependencies older than 30 days
    license_policy:
      denied:
        - GPL-3.0
        - AGPL-3.0

  container:
    enabled: true
    fail_on:
      critical: true
      high: true
    base_image_policy:
      allowed_registries:
        - gcr.io
        - docker.io/library
      max_age_days: 90

  secrets:
    enabled: true
    fail_on_any: true

  iac:
    enabled: true
    fail_on:
      critical: true
      high: true
    frameworks:
      - terraform
      - kubernetes
      - dockerfile
```

### Roll out gradually

Don't flip everything to "block" on day one — developers will get frustrated and the gates will be disabled. Start soft and tighten over a few sprints:

```yaml
# Phase 1: Warn only (Week 1-2)
security_gate_mode: "warn"

# Phase 2: Block critical only (Week 3-4)
security_gate_mode: "block_critical"

# Phase 3: Block critical and high (Week 5+)
security_gate_mode: "block_critical_high"
```

## End-to-end pipeline examples

The examples below wire several gates into a single pipeline. They use per-tool JSON output and simple threshold checks; see [Normalizing multi-scanner output](#normalizing-multi-scanner-output-into-a-single-gate-decision) for a more robust, SARIF-based approach once you have more than a couple of scanners.

### GitHub Actions

```yaml
# .github/workflows/security-gates.yaml
name: Security Gates Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  FAIL_ON_CRITICAL: true
  FAIL_ON_HIGH: true

jobs:
  # Gate 1: Secret Scanning
  secrets-gate:
    name: "Secrets Gate"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@main
        with:
          path: ./
          base: ${{ github.event.repository.default_branch }}
          head: HEAD
          extra_args: --only-verified

      - name: Gitleaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

  # Gate 2: SAST Gate
  sast-gate:
    name: "SAST Gate"
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4

      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with:
          languages: javascript, python  # Adjust based on your languages

      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

      - name: Run Semgrep
        uses: returntocorp/semgrep-action@v1
        with:
          config: >-
            p/security-audit
            p/secrets
            p/owasp-top-ten

      - name: Check SAST Results
        run: |
          # Parse results and fail if critical/high issues found
          if [ -f semgrep.json ]; then
            CRITICAL=$(jq '[.results[] | select(.extra.severity == "ERROR")] | length' semgrep.json)
            if [ "$CRITICAL" -gt 0 ]; then
              echo "Found $CRITICAL critical SAST issues"
              exit 1
            fi
          fi

  # Gate 3: SCA Gate (Dependency Scanning)
  sca-gate:
    name: "SCA Gate"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy SCA Scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'json'
          output: 'trivy-sca-results.json'
          vuln-type: 'library'
          severity: 'CRITICAL,HIGH'

      - name: Evaluate SCA Gate
        run: |
          CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' trivy-sca-results.json)
          HIGH=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' trivy-sca-results.json)

          echo "SCA Results: Critical=$CRITICAL, High=$HIGH"

          if [ "$CRITICAL" -gt 0 ]; then
            echo "SCA Gate FAILED: $CRITICAL critical vulnerabilities found"
            jq '.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL") | {Package: .PkgName, Version: .InstalledVersion, CVE: .VulnerabilityID, Title: .Title}' trivy-sca-results.json
            exit 1
          fi

          if [ "$HIGH" -gt 5 ]; then
            echo "SCA Gate FAILED: More than 5 high vulnerabilities ($HIGH found)"
            exit 1
          fi

          echo "SCA Gate PASSED"

      - name: License Compliance Check
        run: |
          pip install pip-licenses
          pip-licenses --format=json --output-file=licenses.json

          # Check for denied licenses
          DENIED=$(jq '[.[] | select(.License | test("GPL-3.0|AGPL"))] | length' licenses.json)
          if [ "$DENIED" -gt 0 ]; then
            echo "License Gate FAILED: Found $DENIED packages with denied licenses"
            jq '.[] | select(.License | test("GPL-3.0|AGPL"))' licenses.json
            exit 1
          fi
          echo "License Gate PASSED"

  # Gate 4: Container Security Gate
  container-gate:
    name: "Container Gate"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build Container Image
        run: docker build -t ${{ github.repository }}:${{ github.sha }} .

      - name: Run Trivy Container Scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ github.repository }}:${{ github.sha }}'
          format: 'json'
          output: 'trivy-container-results.json'
          severity: 'CRITICAL,HIGH,MEDIUM'

      - name: Evaluate Container Gate
        run: |
          CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' trivy-container-results.json)
          HIGH=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "HIGH")] | length' trivy-container-results.json)

          echo "Container Scan Results: Critical=$CRITICAL, High=$HIGH"

          if [ "$CRITICAL" -gt 0 ]; then
            echo "Container Gate FAILED: $CRITICAL critical vulnerabilities"
            exit 1
          fi

          echo "Container Gate PASSED"

      - name: Dockerfile Best Practices (Hadolint)
        uses: hadolint/hadolint-action@v3.1.0
        with:
          dockerfile: Dockerfile
          failure-threshold: error

  # Gate 5: IaC Security Gate
  iac-gate:
    name: "IaC Gate"
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Checkov IaC Scan
        uses: bridgecrewio/checkov-action@master
        with:
          directory: .
          framework: terraform,kubernetes,dockerfile
          output_format: json
          output_file_path: checkov-results.json
          soft_fail: true

      - name: Evaluate IaC Gate
        run: |
          if [ -f checkov-results.json ]; then
            FAILED=$(jq '.results.failed_checks | length' checkov-results.json 2>/dev/null || echo "0")
            CRITICAL=$(jq '[.results.failed_checks[]? | select(.check_result.evaluated_keys[]? | contains("CRITICAL"))] | length' checkov-results.json 2>/dev/null || echo "0")

            echo "IaC Scan Results: Failed Checks=$FAILED"

            if [ "$CRITICAL" -gt 0 ]; then
              echo "IaC Gate FAILED: Critical misconfigurations found"
              exit 1
            fi
          fi
          echo "IaC Gate PASSED"

  # Final Gate: Aggregate Results
  security-gate-summary:
    name: "Security Gate Summary"
    needs: [secrets-gate, sast-gate, sca-gate, container-gate, iac-gate]
    runs-on: ubuntu-latest
    if: always()
    steps:
      - name: Check Gate Results
        run: |
          echo "## Security Gate Summary" >> $GITHUB_STEP_SUMMARY
          echo "" >> $GITHUB_STEP_SUMMARY

          if [ "${{ needs.secrets-gate.result }}" == "success" ]; then
            echo "Secrets Gate: PASSED" >> $GITHUB_STEP_SUMMARY
          else
            echo "Secrets Gate: FAILED" >> $GITHUB_STEP_SUMMARY
          fi

          if [ "${{ needs.sast-gate.result }}" == "success" ]; then
            echo "SAST Gate: PASSED" >> $GITHUB_STEP_SUMMARY
          else
            echo "SAST Gate: FAILED" >> $GITHUB_STEP_SUMMARY
          fi

          if [ "${{ needs.sca-gate.result }}" == "success" ]; then
            echo "SCA Gate: PASSED" >> $GITHUB_STEP_SUMMARY
          else
            echo "SCA Gate: FAILED" >> $GITHUB_STEP_SUMMARY
          fi

          if [ "${{ needs.container-gate.result }}" == "success" ]; then
            echo "Container Gate: PASSED" >> $GITHUB_STEP_SUMMARY
          else
            echo "Container Gate: FAILED" >> $GITHUB_STEP_SUMMARY
          fi

          if [ "${{ needs.iac-gate.result }}" == "success" ]; then
            echo "IaC Gate: PASSED" >> $GITHUB_STEP_SUMMARY
          else
            echo "IaC Gate: FAILED" >> $GITHUB_STEP_SUMMARY
          fi

      - name: Fail if Any Gate Failed
        if: |
          needs.secrets-gate.result == 'failure' ||
          needs.sast-gate.result == 'failure' ||
          needs.sca-gate.result == 'failure' ||
          needs.container-gate.result == 'failure' ||
          needs.iac-gate.result == 'failure'
        run: |
          echo "One or more security gates failed. Blocking deployment."
          exit 1
```

### GitLab CI

```yaml
# .gitlab-ci.yml
stages:
  - security-scan
  - security-gate
  - build
  - deploy

variables:
  SECURITY_GATE_CRITICAL_THRESHOLD: 0
  SECURITY_GATE_HIGH_THRESHOLD: 0

# Secret Scanning Gate
secrets-scan:
  stage: security-scan
  image: trufflesecurity/trufflehog:latest
  script:
    - trufflehog git file://. --only-verified --json > secrets-report.json
    - |
      SECRETS_FOUND=$(cat secrets-report.json | wc -l)
      if [ "$SECRETS_FOUND" -gt 0 ]; then
        echo "Secrets detected in repository"
        cat secrets-report.json
        exit 1
      fi
  artifacts:
    reports:
      secret_detection: secrets-report.json

# SAST Gate
sast-scan:
  stage: security-scan
  image: returntocorp/semgrep
  script:
    - semgrep scan --config=p/security-audit --config=p/owasp-top-ten --json -o semgrep-report.json .
  artifacts:
    paths:
      - semgrep-report.json
    reports:
      sast: semgrep-report.json

# Container Scanning Gate
container-scan:
  stage: security-scan
  image:
    name: aquasec/trivy:latest
    entrypoint: [""]
  script:
    - trivy image --format json --output trivy-report.json $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  artifacts:
    paths:
      - trivy-report.json
    reports:
      container_scanning: trivy-report.json

# Security Gate Evaluation
security-gate:
  stage: security-gate
  image: alpine:latest
  needs:
    - secrets-scan
    - sast-scan
    - container-scan
  before_script:
    - apk add --no-cache jq
  script:
    - |
      echo "Evaluating Security Gates..."

      # Check SAST results
      if [ -f semgrep-report.json ]; then
        SAST_CRITICAL=$(jq '[.results[]? | select(.extra.severity == "ERROR")] | length' semgrep-report.json)
        if [ "$SAST_CRITICAL" -gt "$SECURITY_GATE_CRITICAL_THRESHOLD" ]; then
          echo "SAST Gate Failed: $SAST_CRITICAL critical issues found"
          exit 1
        fi
      fi

      # Check Container results
      if [ -f trivy-report.json ]; then
        CONTAINER_CRITICAL=$(jq '[.Results[]?.Vulnerabilities[]? | select(.Severity == "CRITICAL")] | length' trivy-report.json)
        if [ "$CONTAINER_CRITICAL" -gt "$SECURITY_GATE_CRITICAL_THRESHOLD" ]; then
          echo "Container Gate Failed: $CONTAINER_CRITICAL critical vulnerabilities"
          exit 1
        fi
      fi

      echo "All Security Gates Passed"
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH
```

### Interpreting gate results

A good gate summary tells the developer what failed, where, and what to do next:

```text
Security Gate Summary
========================
+----------------+--------+---------+
| Gate           | Status | Issues  |
+----------------+--------+---------+
| Secrets        | PASS   | 0       |
| SAST           | PASS   | 3 (low) |
| SCA            | WARN   | 2 (med) |
| Container      | PASS   | 0       |
| IaC            | FAIL   | 1 (crit)|
+----------------+--------+---------+

Pipeline blocked: IaC gate failed
   - CKV_AWS_21: S3 bucket has public access enabled
   - File: terraform/s3.tf:15

Action Required: Fix the critical IaC issue before merge.
```

When a gate fails: check the CI logs (most tools show exactly what is wrong and where), fix it or file an exception if it is a false positive, then re-run the pipeline.

## Normalizing multi-scanner output into a single gate decision

Real pipelines rarely run a single scanner. A typical SCA stage, for example, might run both an application dependency scanner (e.g., OSV-Scanner) and a container/SBOM scanner (e.g., Trivy) to get broader vulnerability database coverage. Each tool produces its own result, its own exit code semantics, and its own idea of "severity". Without normalization, you end up with N independent pass/fail signals instead of one gate decision, and inconsistent exit code handling across tools becomes a silent source of false negatives.

### Standardize on SARIF as the common interface

Most modern scanners can emit [SARIF](https://sarifweb.azurewebsites.net/) (Static Analysis Results Interchange Format). SARIF's `security-severity` property (under each rule's `properties`) is typically populated with a CVSS-like score, which gives you a single numeric field to gate on regardless of which tool produced the finding.

```python
# Read every SARIF file produced by the pipeline's scanners and
# return the single highest security-severity score found across all of them.
import json
import logging

def max_severity(sarif_paths: list[str]) -> float:
    max_score = 0.0
    for path in sarif_paths:
        try:
            with open(path) as f:
                sarif = json.load(f, strict=False)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            logging.error(f"Failed to parse SARIF file {path}: {e}")
            return -1.0 # Explicitly signal a tool ERROR state

        for run in sarif.get("runs", []):
            rules = run.get("tool", {}).get("driver", {}).get("rules", [])
            severities = {
                r.get("id"): r.get("properties", {}).get("security-severity")
                for r in rules if r.get("id")
            }
            for result in run.get("results", []):
                score = severities.get(result.get("ruleId"))
                if score is not None:
                    try:
                        max_score = max(max_score, float(score))
                    except ValueError:
                        logging.warning(f"Invalid security-severity value: {score}")
                        continue

    return max_score
```

### Map the score to a gate decision

```python
def gate_status(score: float) -> str:
    if score < 0.0:
        return "ERROR"      # tool crashed or output is malformed
    if score >= 8.0:
        return "FAILED"     # block the pipeline
    if score >= 5.0:
        return "WARNING"    # log only, do not block
    return "PASSED"
```

| Status | Meaning | Blocks the pipeline? |
|---|---|---|
| `PASSED` | Highest score across all scanners is below 5.0 | No |
| `WARNING` | Highest score is 5.0 to 7.9 | No (logged only) |
| `FAILED` | Highest score is 8.0 or above | **Yes** |
| `ERROR` | A scanner crashed, subprocess failed, or produced malformed SARIF | **Yes** |

The thresholds above (5.0, 8.0) are examples, not a prescribed standard. Each organization should set its own thresholds based on its risk tolerance, the criticality of the affected system, and its remediation capacity.

Treating "scanner crashed" as its own `ERROR` state, distinct from `FAILED`, matters: a gate that only checks whether anything failed on severity will silently pass a pipeline where a scanner never actually ran.

### The exit code trap

Do not assume a non-zero exit code always means vulnerabilities were found, or that zero always means the scan is clean. Exit code semantics differ per tool and must be normalized individually. For example, OSV-Scanner uses exit code `1` to mean "scan completed, vulnerabilities were found," not a tool failure. Treating that as a pipeline error would incorrectly flag every scan with findings as broken, rather than letting the SARIF based gate decide pass, warn, or fail on its own terms:

```python
def run_osv_scanner(cmd: list[str]) -> int:
    exit_code = subprocess.run(cmd).returncode
    if exit_code == 1:
        # OSV-Scanner returns 1 when vulnerabilities are found, not a crash.
        # The real pass/warn/fail decision comes later, from the SARIF scores.
        return 0
    return exit_code
```

Each scanner's documentation should be checked individually for this distinction before wiring it into a gate. Some tools, like Trivy by default, exit `0` regardless of findings, so any non-zero exit from them is a genuine tool failure.

### Enforcing the gate in CI

Once the orchestrator has parsed the SARIF files and determined the final severity score, it must translate that decision into a pipeline action. In CI/CD environments (like GitHub Actions, GitLab CI, or Jenkins), this is achieved by exiting the orchestrator script with a non-zero exit code to block the merge or deployment.

```python
import sys

def enforce_pipeline_gate(status: str):
    """
    Halts the CI pipeline if the status is FAILED or ERROR.
    """
    if status in ("FAILED", "ERROR"):
        # Writing to stderr ensures CI systems prominently display the failure reason
        print(f"::error::Security gate {status}. Halting pipeline.", file=sys.stderr)
        sys.exit(1) 
    
    print(f"Security gate {status}. Pipeline may proceed.")
    sys.exit(0)
```

## Exception and risk-acceptance process

No gate system survives contact with reality without an exception process. Without one, developers disable gates rather than deal with blocked pipelines. A sound process:

1. **Raise an exception request** — the developer (or team) documents the finding, explains why immediate remediation is not feasible (e.g., no fix available, legacy library), and proposes a compensating control.
2. **Approve with a risk owner** — a security engineer or application security lead reviews and approves; the approver takes ownership of the accepted risk.
3. **Time-box every exception** — set a hard expiry (e.g., 30 or 90 days). The gate re-engages automatically when the exception expires. Indefinite exceptions are not exceptions — they are hidden vulnerabilities.
4. **Track exceptions centrally** — maintain a register (in a vulnerability management tool or ticketing system) so accepted risks are visible to leadership, not hidden in `.semgrepignore` files.
5. **Review on a cadence** — include open exceptions in sprint planning and quarterly security reviews so they get addressed, not forgotten. Report exception counts and age to leadership as a risk indicator.

### Exceptions as code

Where the exception register lives in the repository (in addition to, not instead of, a central register), make every entry carry a reason, an approver, a tracking ticket, and an expiry so the gate can re-engage automatically:

```yaml
# .security-exceptions.yaml
exceptions:
  - id: "CVE-2023-12345"
    reason: "False positive - not applicable to our usage"
    approved_by: "security-team"
    expires: "2024-06-01"

  - id: "semgrep-rule-xyz"
    reason: "Accepted risk - compensating controls in place"
    approved_by: "security-team"
    jira_ticket: "SEC-123"
    expires: "2024-03-15"
```

### Emergency bypass (use sparingly)

Sometimes production is down and the fix has to ship. Provide an explicit, audited bypass path that requires a named approver and a manual step — never a silent `continue-on-error`. Every bypass should produce a ticket that tracks when the gate is re-enabled:

```yaml
# Emergency bypass (requires approval)
deploy-production:
  rules:
    - if: $SECURITY_BYPASS == "true" && $APPROVED_BY != ""
      when: manual
      allow_failure: false
    - if: $SECURITY_GATES_PASSED == "true"
      when: on_success
```

## Smarter prioritization

Mature programs increasingly drive gates from **correlated, contextual risk** rather than isolated scanner output. Application Security Posture Management ([ASPM](../../3-Governance/3-3-Reporting/3-3-3-ASPM.md)) aggregates findings across tools, deduplicates them, and adds code-to-runtime context so gates block on what is genuinely exploitable and reachable in production — keeping signal high and friction low.

The evolution of gate intelligence:

| Generation | What drives the gate |
|---|---|
| 1st | Raw count of findings above a severity threshold |
| 2nd | New findings since baseline, filtered by severity |
| 3rd | CVSS + EPSS + KEV — exploitability-weighted severity |
| 4th | Reachability + runtime exposure + ASPM correlation |

## Common pitfalls and anti-patterns

- **Gates without feedback** — a gate that blocks with no explanation sends developers to Google. Every blocked gate must link to the finding, the affected code, and remediation guidance.
- **Gates configured but not enforced** — required CI status checks must be enabled in branch protection rules; otherwise developers merge without them.
- **Relying on a single scanner** — no scanner catches everything. Layer multiple tools and normalize their output into one decision rather than trusting one vendor's view of severity.
- **Slow gates** — scans add time. Run them in parallel, cache databases and dependencies, and keep PR-stage scans diff-aware, or developers will route around the slow pipeline.
- **Exception process that requires security team approval for every finding** — creates a bottleneck and incentivizes teams to avoid scanning. Delegate tier-2 and tier-3 exception approvals to risk owners within the product team.
- **No visibility into exception trends** — if the exception register is growing every sprint, that is a systemic problem. Track exception counts, ages, and owners as board-level metrics.
- **Unaudited bypasses** — if someone needs an emergency bypass, make sure there is a ticket tracking who approved it and when it expires.
- **Suppression via comments in source code** — `# nosec`, `// NOSONAR`, and `.semgrepignore` suppressions are invisible in most dashboards. Require that suppressions be tracked in the central exception register.

## Maturity progression

**Starter** — Enable SAST and SCA scans in CI. Run in advisory mode (report, don't block) for two sprints to establish baseline. Then block on new criticals.

**Intermediate** — Gate pull requests on new high/critical SAST and SCA findings. Enforce a formal exception process. Track exceptions in DefectDojo or Jira. Add container scan gates at the build stage.

**Advanced** — Drive gates from ASPM-correlated, reachability-enriched findings. Fully automate exception expiry. Measure false positive rate per scanner and tune quarterly. Report gate compliance and exception trends to engineering leadership monthly.

## Tools

| Category | Examples |
|---|---|
| Vulnerability tracking & gate integration | DefectDojo (open source), OWASP Dependency-Track (open source), Archery |
| Scan orchestration | SecureCodeBox (open source, Kubernetes-native) |
| Policy-as-code gate enforcement | OPA/Conftest, Rego policies in CI, Kyverno (Kubernetes) |
| CI/CD native gates | GitHub branch protection + required status checks, GitLab merge request approvals, Jenkins Quality Gates |
| Commercial platforms with policy gates | Snyk, Checkmarx, Veracode |
| ASPM (correlated gate decisions) | Apiiro, Arnica, Ox Security, Cycode — see [ASPM](../../3-Governance/3-3-Reporting/3-3-3-ASPM.md) |
| Exception / risk-acceptance tracking | Jira (security issue type), ServiceNow, DefectDojo risk acceptance workflow |

## Metrics and KPIs

| Metric | Target |
|---|---|
| % of PRs passing security gates without exception | > 95% |
| Open exceptions older than 90 days | 0 |
| Gate false positive rate | < 15% per tool |
| Findings that escape to production | Decreasing quarter-over-quarter |
| Mean time from gate block to resolution | < 3 business days (critical) |

---

## Further reading

- [OWASP DSOMM — Test & Verification](https://dsomm.owasp.org/)
- [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [NIST SSDF — PW & RV practices](https://csrc.nist.gov/Projects/ssdf)
- [NIST SP 800-218: Secure Software Development Framework](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [CIS Software Supply Chain Security Guide](https://www.cisecurity.org/insights/white-papers/cis-software-supply-chain-security-guide)
- [DefectDojo documentation](https://defectdojo.github.io/django-DefectDojo/)
