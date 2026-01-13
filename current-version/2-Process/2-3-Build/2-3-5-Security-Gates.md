# Security Gates

Security gates are checkpoints in your CI/CD pipeline that block or warn when security issues are detected. Think of them like quality gates, but for security - if a scan finds a critical vulnerability, the pipeline stops and the code doesn't get deployed.

The idea is simple: catch problems before they hit production. A vulnerability found during a pull request costs minutes to fix. The same vulnerability found in production? That's an incident, potentially a breach, and weeks of cleanup.

## Why Bother?

Most teams already run linters and unit tests in CI. Security gates extend this to:

- Block code with hardcoded secrets or API keys
- Catch vulnerable dependencies before they ship
- Flag container images with known CVEs
- Enforce infrastructure-as-code policies (no public S3 buckets, etc.)

Without gates, security becomes a manual review bottleneck or gets skipped entirely when deadlines hit.

## Types of Security Gates

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

## Setting Up Security Gates

### Define Your Thresholds First

Before wiring up tools, decide what blocks a deployment vs. what just logs a warning. Here's a common starting point:

| Severity | Action | Example Threshold |
|----------|--------|-------------------|
| Critical | Block deployment | 0 allowed |
| High | Block deployment | 0 allowed |
| Medium | Warn, require approval | 5 or fewer allowed |
| Low | Warn only | No limit (track) |

### Centralized Config

Keep your gate policies in a single config file so teams know what's enforced:

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

### GitHub Actions Example

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

### GitLab CI Example

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

## Tips From the Field

### Roll Out Gradually

Don't flip everything to "block" on day one - you'll just frustrate developers and get the gates disabled. Start soft:

```yaml
# Phase 1: Warn only (Week 1-2)
security_gate_mode: "warn"

# Phase 2: Block critical only (Week 3-4)
security_gate_mode: "block_critical"

# Phase 3: Block critical and high (Week 5+)
security_gate_mode: "block_critical_high"
```

### Handle False Positives

Scanners aren't perfect. You'll need a way to suppress findings that don't apply:

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

### Emergency Bypass (Use Sparingly)

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

## Interpreting Security Gate Results

### Sample Gate Output

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

### When a Gate Fails

1. Check the CI logs - most tools show exactly what's wrong and where
2. Fix it or file an exception if it's a false positive
3. Re-run the pipeline

## Watch Out For

- **False positives will happen** - have an exception process ready or developers will just disable the gates
- **No scanner catches everything** - layer multiple tools, don't rely on just one
- **Scans add time** - run them in parallel and cache where possible, or developers will complain about slow pipelines
- **Audit your bypasses** - if someone needs an emergency bypass, make sure there's a ticket tracking when it expires

---

## Tools[^1]

### Open-source

- [DefectDojo](https://github.com/DefectDojo/django-DefectDojo) - Security orchestration and vulnerability management platform
- [OWASP Dependency-Track](https://dependencytrack.org/) - Component analysis platform for managing vulnerabilities
- [SecureCodeBox](https://www.securecodebox.io/) - Kubernetes-native security scanning orchestration

### Commercial

- [Snyk](https://snyk.io/) - Developer security platform with policy gates
- [Checkmarx](https://checkmarx.com/) - Application security testing with quality gates
- [Veracode](https://www.veracode.com/) - Application security with policy enforcement

---

## References

- [NIST SP 800-218: Secure Software Development Framework](https://csrc.nist.gov/publications/detail/sp/800-218/final)
- [OWASP DevSecOps Guidelines](https://owasp.org/www-project-devsecops-guideline/)
- [CIS Software Supply Chain Security Guide](https://www.cisecurity.org/insights/white-papers/cis-software-supply-chain-security-guide)

[^1]: Listed in alphabetical order.
