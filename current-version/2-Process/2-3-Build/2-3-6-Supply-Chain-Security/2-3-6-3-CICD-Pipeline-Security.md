# CI/CD Pipeline Security

The pipeline that builds and ships your software is itself a high-value target. It holds powerful credentials, executes code from many sources, and has direct access to production. Attackers increasingly go after the pipeline rather than the application — a single poisoned build can compromise every downstream consumer. Securing the pipeline is therefore as important as securing the code it builds.

## The threat model: OWASP Top 10 CI/CD Security Risks

The [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/) is the canonical reference. Key risks include:

- **Insufficient flow control mechanisms (CICD-SEC-1)** — the ability to push code or artifacts to production without adequate review or gates. Anyone who can merge to main can deploy to production.
- **Poisoned Pipeline Execution / PPE (CICD-SEC-3)** — injecting malicious commands into the build by manipulating pipeline configuration or scripts. Example: a PR modifies a GitHub Actions workflow file to exfiltrate secrets to an external URL. Defense: require reviews for workflow file changes; use `pull_request_target` carefully.
- **Dependency-chain abuse (CICD-SEC-6)** — dependency confusion, typosquatting, and malicious packages pulled during the build. The pipeline's package manager runs with the same trust as CI secrets.
- **Insufficient credential hygiene (CICD-SEC-4)** — long-lived, over-privileged secrets exposed to pipeline steps; secrets printed to logs; secrets shared across environments.
- **Ungoverned usage of third-party services (CICD-SEC-8)** — unvetted GitHub Actions, Jenkins plugins, and integrations running with access to the pipeline and its credentials.
- **Insufficient PBAC / pipeline-based access controls (CICD-SEC-2)** — runners and jobs with far more access than they need; secrets available to all jobs in a repository.

## Hardening the pipeline

### Least-privilege tokens

Scope permissions explicitly and narrowly. Every permission not granted is a capability an attacker cannot abuse:

```yaml
# GitHub Actions: explicit minimal permissions
permissions:
  contents: read        # read source code only
  packages: write       # push to GitHub Packages
  id-token: write       # request OIDC token for keyless signing
  # All other permissions are denied by default
```

### OIDC workload identity — replace long-lived secrets

Exchange short-lived OIDC tokens for cloud credentials instead of storing long-lived cloud access keys as CI secrets:

```yaml
- name: Configure AWS credentials via OIDC
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/ci-deploy
    aws-region: us-east-1
    # No AWS_ACCESS_KEY_ID or AWS_SECRET_ACCESS_KEY needed
```

The OIDC token is valid for minutes and cannot be reused; a leaked token expires before it can be weaponized.

### Pin third-party Actions to immutable commit SHAs

Tags like `@v3` are mutable — they can be silently redirected to malicious code. Pin to the commit digest:

```yaml
# Mutable tag — do not use this in production
- uses: actions/checkout@v4

# Immutable SHA pin — use this
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

Use tools like Dependabot or Renovate to automate SHA pin updates as new versions are released.

### Harden runners

- **Ephemeral, isolated runners** — use ephemeral GitHub-hosted or self-hosted runners that start clean and are destroyed after each job. Persistent runners accumulate state that attackers can abuse.
- **Network egress control** — restrict what external hosts runners can reach during a build. A build that only needs npm and GitHub should not be able to reach arbitrary cloud APIs. Use StepSecurity Harden-Runner for GitHub Actions:

  ```yaml
  - uses: step-security/harden-runner@v2
    with:
      egress-policy: block
      allowed-endpoints: >
        registry.npmjs.org:443
        api.github.com:443
  ```

- **Secrets scoping** — in GitHub, environment secrets are only available to workflow jobs that target that environment; use environment protection rules to gate access.

### Protect fork/PR workflows

Pull requests from forks are a common PPE vector. Apply these controls:

- Require approval before running CI on first-time contributor PRs (`pull_request` trigger does not have access to secrets; `pull_request_target` does and must be used carefully).
- Never expose secrets to untrusted PRs.
- Protect workflow files with CODEOWNERS so any change to `.github/workflows/` requires security team review.

### Pipeline configuration as a security perimeter

The pipeline definition (`.github/workflows/`, `Jenkinsfile`, `.gitlab-ci.yml`) is executable code. Treat it accordingly:

- Require pull request reviews for workflow file changes.
- Use `CODEOWNERS` to route changes to security-aware reviewers.
- Scan workflow files with zizmor or semgrep-rules for CI to catch common vulnerabilities (script injection, unsafe `pull_request_target` usage).

## Measure and enforce continuously

Use automated tooling to keep the pipeline hardened over time — egress monitoring on runners, workflow static analysis, and repository security scoring — and feed the results into your governance program. A hardened pipeline today can drift back to a vulnerable state without continuous enforcement.

OpenSSF Scorecard provides a free, automated security score for open-source repositories that covers many pipeline hygiene dimensions (branch protection, dependency pinning, SAST, signing):

```bash
scorecard --repo=github.com/myorg/myrepo --format json | jq .checks
```

## Common pitfalls and anti-patterns

- **Secrets stored as plain-text environment variables in pipeline config** — anyone who can read the pipeline file can read the secret. Use the platform's secret store, not inline values.
- **One long-lived AWS/GCP key for all CI jobs** — a single leaked key compromises every environment. Move to OIDC with per-environment roles.
- **`pull_request_target` with unchecked-out code from the fork** — this gives fork PRs access to secrets. This is the most common PPE vulnerability in GitHub Actions.
- **Third-party Actions from unverified authors** — an Action with write access to the workspace and access to secrets can exfiltrate credentials. Audit every third-party Action used.
- **No egress control on runners** — a compromised runner with unrestricted internet access can quietly exfiltrate secrets or establish C2 connections.
- **Security scans disabled "temporarily" in CI** — "temporary" disables become permanent. Protect security step configurations in CODEOWNERS just as you protect workflow files.

## Maturity progression

**Starter** — Enable branch protection on main (require PR reviews, status checks). Move cloud credentials to OIDC workload identity. Set explicit `permissions:` blocks on all workflow jobs. Audit the list of third-party Actions in use.

**Intermediate** — Pin all third-party Actions to SHA digests (use Dependabot to manage). Add CODEOWNERS for `.github/workflows/`. Deploy StepSecurity Harden-Runner with egress monitoring. Add zizmor or Semgrep CI rules to scan workflow files. Score repositories with OpenSSF Scorecard and set minimum score targets.

**Advanced** — Enforce egress allowlists (block mode) on all runners. Use ephemeral, isolated self-hosted runners for sensitive builds. Sign all pipeline outputs (see [Artifact Signing and Provenance](2-3-6-2-Artifact-Signing-and-Provenance.md)). Automate Allstar policy enforcement across the GitHub organization. Report pipeline security score trends to engineering leadership quarterly.

## Metrics and KPIs

| Metric | Target |
|---|---|
| % of repositories with branch protection on main | 100% |
| % of CI jobs using OIDC (no long-lived cloud keys) | 100% |
| % of third-party Actions pinned to SHA digest | 100% |
| OpenSSF Scorecard average across organization | > 7.0 / 10 |
| Repositories with unreviewed workflow file changes | 0 |
| Egress violations detected on runners | Tracked; alerts on anomalies |

---

## Tools[^1]

### Open-source

- [Allstar](https://github.com/ossf/allstar) - Enforces security policies across GitHub organizations (branch protection, binary artifacts, SECURITY.md, outside collaborators); alerts or opens issues on violations.
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) - Scores repositories on supply-chain security best practices across 20+ checks; integrates as a GitHub Actions workflow with badge support.
- [StepSecurity Harden-Runner](https://github.com/step-security/harden-runner) - Egress filtering and runtime security for GitHub Actions runners; monitors and optionally blocks unauthorized outbound connections.
- [zizmor](https://github.com/woodruffw/zizmor) - Static analysis tool for GitHub Actions workflow security vulnerabilities (script injection, PPE patterns, dangerous triggers).

### Commercial

- [Cycode](https://cycode.com/) - Application security and pipeline/supply-chain protection; detects misconfigured pipelines and enforces policy across GitHub, GitLab, and Bitbucket.
- [Legit Security](https://www.legitsecurity.com/) - Security posture management for the software factory; maps every pipeline, detects risky configurations, and tracks pipeline security posture over time.

---

### Links

[^1]: Listed in alphabetical order.
