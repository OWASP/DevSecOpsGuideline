# Security in CI/CD Training

Secure coding protects the application; this training protects the **pipeline that builds and ships it**. CI/CD systems hold powerful credentials, run untrusted code, and pull in third-party dependencies and plugins — which makes them a prime target. High-profile breaches (e.g. SolarWinds, Codecov, and numerous compromised GitHub Actions) all abused the build and delivery pipeline rather than the application itself.

Everyone who writes pipeline configuration — developers, platform engineers, SREs — needs to understand how these systems are attacked and how to harden them.

## Why the pipeline is a high-value target

Attackers target pipelines because the payoff is enormous: a single compromised build pipeline can simultaneously poison every artifact it produces, exfiltrate source code and secrets, and grant lateral movement into production environments — all through a mechanism that runs automatically on every push. The SolarWinds attack compromised the build system and inserted malicious code into signed, trusted software updates delivered to 18,000+ customers. Understanding this threat model is the starting point for CI/CD security training.

## What to teach

### The CI/CD threat model

Cover the [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/) in depth — particularly the risks that are non-obvious to developers:

- **CICD-SEC-1 — Insufficient Flow Control**: No merge approval requirements; direct pushes to the main branch; no separation of duties in release pipelines.
- **CICD-SEC-2 — Inadequate Identity and Access Management**: Long-lived tokens with broad scope; no OIDC; shared service accounts; no token rotation.
- **CICD-SEC-3 — Dependency Chain Abuse**: Typosquatting, dependency confusion attacks, compromised transitive dependencies (e.g. `event-stream`).
- **CICD-SEC-4 — Poisoned Pipeline Execution (PPE)**: Untrusted code from a fork PR running in a privileged context with access to secrets. This is one of the most common and impactful CI/CD vulnerabilities.
- **CICD-SEC-6 — Insufficient Credential Hygiene**: Long-lived secrets in environment variables, visible in build logs, or stored as plaintext in configuration files.

### Secrets handling

The single most common and damaging pipeline security failure is credential exposure:

- **Never hardcode** credentials, API keys, or tokens in pipeline configuration or code. Use the CI/CD platform's secret management (GitHub Secrets, GitLab CI/CD variables, Vault).
- Use **OIDC workload identity** where possible — the pipeline authenticates to cloud providers using a short-lived, automatically rotated OIDC token rather than a stored key. No secret to leak, no secret to rotate manually.

  ```yaml
  # GitHub Actions: OIDC to AWS — no long-lived key required
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-actions-role
      aws-region: us-east-1
  ```

- Scope secrets to the minimum: a deployment token should only be able to deploy, not read source code or manage IAM.
- Audit secret access logs; rotate any secret that may have been exposed in a log or error message.

See [Secrets Management](../../2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md) for a comprehensive treatment.

### Least privilege in pipeline jobs

```yaml
# GitHub Actions: least-privilege permissions block — deny all by default
permissions:
  contents: read       # read source code only
  packages: write      # push to GHCR only
  id-token: write      # OIDC token for cloud auth only
```

Teach developers to:
- Always declare an explicit `permissions:` block; never rely on the workflow-level default which may be overly broad.
- Audit what each job actually needs and remove anything it does not use.
- Treat pipeline tokens like production credentials — they often have equivalent or greater blast radius.

### Pinning and provenance

```yaml
# Unpinned (dangerous) — the tag can be moved at any time
- uses: actions/checkout@v4

# Pinned to an immutable digest (safe)
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683  # v4.2.2
```

Teach developers that mutable tags on third-party Actions and container images are a supply-chain attack surface. A tag can be updated without warning to point to a malicious commit.

### Runner hardening

- Use **ephemeral runners** that are created fresh for each job and destroyed immediately after. A persistent runner accumulates state (secrets cached in memory, files on disk) that can be extracted by later jobs.
- **Restrict network egress** — a build job that can reach any internet host can be used for DNS exfiltration or to phone home to attacker infrastructure. Allowlist the registries and package sources the build actually needs.
- Treat self-hosted runners as **sensitive production infrastructure**: harden the OS, apply updates, monitor for anomalous processes, and rotate host credentials regularly.

### Reading and triaging scanner output

Not all developers arrive with the ability to interpret SAST, SCA, and IaC scanner results. Train them to:

- Understand what each scanner type finds and where it has blind spots.
- Distinguish true positives from false positives using the context the scanner cannot see.
- Triage by severity, exploitability, and reachability — not raw counts.
- Route findings to the right owner (fix it themselves vs escalate to AppSec vs accept with documentation).

## How to deliver it

- Bake examples into the team's **actual** pipeline templates so lessons map to real configuration they will modify.
- Pair training with a hardened **paved-road** pipeline so the secure way is also the default way — developers who understand why the template is structured the way it is maintain it better.
- Use realistic exercises: have teams find and fix a poisoned-pipeline or leaked-token scenario in a safe environment.
- Keep platform and security engineers especially current — they design the controls everyone else inherits, so a gap in their knowledge propagates.

## Common pitfalls

- **Treating CI/CD security as "security team's problem"** — pipeline configuration is written by developers and platform engineers. They must own its security.
- **Long-lived tokens everywhere** — the path of least resistance is to create a PAT with broad scope and paste it into every pipeline. OIDC workload identity eliminates this pattern.
- **Never reviewing third-party Actions** — accepting a GitHub Actions update without reviewing what changed is equivalent to accepting a code change without review.
- **No egress monitoring** — without monitoring outbound network connections from runners, a data exfiltration via DNS or HTTP to an attacker-controlled host is invisible.
- **Shared self-hosted runners across security boundaries** — if a fork PR from an external contributor can run code on a self-hosted runner that also serves internal jobs, the isolation has been broken.

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Secrets not hardcoded in pipeline config; branch protection enforced; SAST and SCA runs in CI |
| Developing | OIDC workload identity for cloud auth; Actions pinned to commit SHA; ephemeral runners for sensitive jobs |
| Maturing | Egress filtering on runners; Harden-Runner or equivalent monitoring; regular third-party Action audits |
| Advanced | Hermetic builds; full provenance generation (SLSA Level 2+); pipeline scanned with zizmor or similar; runner compromise detection |

---

## Tools[^1]

### Open-source

- [OpenSSF Scorecard](https://github.com/ossf/scorecard) — Automated checks for security best practices on a repository: dependency pinning, branch protection, code review, vulnerability disclosure. Useful as a teaching baseline and a continuous metric.
- [StepSecurity Harden-Runner](https://github.com/step-security/harden-runner) — Network egress monitoring and runtime security for GitHub Actions runners. Generates an allowlist of outbound connections observed during the build, making unexpected calls visible.
- [zizmor](https://github.com/woodruffw/zizmor) — Static analysis for GitHub Actions workflow files. Detects PPE risks, overly broad permissions, unpinned Actions, and other configuration vulnerabilities.
- [actionlint](https://github.com/rhysd/actionlint) — A linter for GitHub Actions workflow files that catches syntax and logical errors before they hit CI.

### Commercial

- [GitHub Advanced Security](https://github.com/security/advanced-security) — Secret scanning, code scanning (CodeQL SAST), Dependabot SCA, and supply-chain features (dependency review, signing) integrated into GitHub.
- [GitLab Ultimate](https://about.gitlab.com/pricing/) — Built-in pipeline security scanning (SAST, DAST, SCA, secrets, container scanning) and compliance pipeline features baked into GitLab CI.

---

### Links

[^1]: Listed in alphabetical order.
