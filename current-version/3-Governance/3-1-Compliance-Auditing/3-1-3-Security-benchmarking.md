# Security Benchmarking

Security benchmarking measures your security posture against an objective standard — either an external best-practice baseline or your own past performance. Benchmarks answer two questions every program eventually faces: "How do we compare to recognized good practice?" and "Are we getting better over time?" Without them, security investment is guided by intuition rather than evidence.

## Types of benchmarks

- **Configuration benchmarks** — [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) provide prescriptive, consensus hardening baselines for operating systems, cloud, containers, and Kubernetes. Each check is categorized as Level 1 (essential, low-impact) or Level 2 (defense-in-depth, may affect usability). Measuring against them produces a concrete compliance percentage you can track over time.
- **Supply-chain posture** — [OpenSSF Scorecard](https://github.com/ossf/scorecard) scores open-source and internal repositories on supply-chain security practices: branch protection, pinned dependencies, signed releases, fuzzing, and more. Run it in CI on every pull request and on a regular schedule across all repos.
- **Maturity models** — [OWASP SAMM](https://owaspsamm.org/), [OWASP DSOMM](https://dsomm.owasp.org/), and [BSIMM](https://www.bsimm.com/) assess how mature your overall program is across many practices, and allow comparison to industry peers.
- **Cloud security posture** — tools like Prowler and cloud-native services (AWS Security Hub, Azure Defender, GCP Security Command Center) continuously benchmark your cloud configuration against CIS, PCI DSS, ISO 27001, and other standards.

## Choosing the right benchmark for the job

| What you're measuring | Best benchmark |
|---|---|
| OS and server hardening | CIS Benchmarks (Linux, Windows, macOS) |
| Kubernetes cluster security | CIS Kubernetes Benchmark, kube-bench |
| Cloud account configuration | CIS AWS/Azure/GCP Foundations, Prowler |
| Source code repository health | OpenSSF Scorecard |
| DevSecOps pipeline maturity | OWASP DSOMM |
| Overall AppSec program maturity | OWASP SAMM, BSIMM |
| Container image hardening | CIS Docker Benchmark, Trivy (misconfig) |

## CIS Benchmark scoring — a worked example

CIS Benchmarks produce a pass/fail result for each check. Consider the CIS Kubernetes Benchmark for a cluster control plane:

```
[PASS] 1.1.1 Ensure that the API server pod specification file permissions are set to 644 or more restrictive
[FAIL] 1.2.6 Ensure that the --authorization-mode argument is not set to AlwaysAllow
[PASS] 1.2.9 Ensure that the admission control plugin EventRateLimit is set
[FAIL] 4.2.1 Ensure that the kubelet service file permissions are set to 644 or more restrictive
```

A typical run might yield 60/80 checks passing = 75%. The actionable output is not the percentage — it is the list of failing checks, each with a remediation step. Prioritize failing checks by Level (Level 1 first) and by risk impact (auth/authz failures before filesystem permissions).

Over quarters, track the delta: 75% → 82% → 91%. This is the story that justifies the hardening investment.

## Using OpenSSF Scorecard — step by step

Scorecard evaluates 20+ checks across a repository. Running it is straightforward:

```bash
# Run against your repo (requires GitHub token with read scope)
GITHUB_AUTH_TOKEN=<token> scorecard --repo github.com/myorg/myrepo

# Or run as a GitHub Actions workflow (auto-triggered on push)
# Add the scorecard-action workflow from github.com/ossf/scorecard-action
```

A sample output with scores per check:

```
Maintained:           10 / 10
Code-Review:           8 / 10  (some PRs merged without review)
Dangerous-Workflow:   10 / 10
Dependency-Update-Tool: 10 / 10 (Dependabot enabled)
Binary-Artifacts:     10 / 10
Branch-Protection:     7 / 10  (no require-signed-commits)
Pinned-Dependencies:   3 / 10  (Actions not pinned to SHA)
SAST:                  5 / 10  (SAST runs but no blocking gate)
Signed-Releases:       0 / 10  (no signed releases)

Aggregate score: 7.0 / 10
```

From this output, actionable priorities are clear: pin Actions to SHA digests (Pinned-Dependencies: 3/10), add signed releases (Signed-Releases: 0/10), and require signed commits in branch protection (Branch-Protection: 7/10). These three fixes would move the aggregate score above 9.0.

## DSOMM assessment process

OWASP DSOMM provides a web-based tool and YAML-based data model for tracking pipeline practices. A practical assessment process:

1. **Install the DSOMM application** — run it locally or self-host with Docker.
2. **Select your dimensions** — DSOMM covers Static Depth, Dynamic Depth, Intensity, Consolidation, and more. Start with Static Depth (SAST, SCA) and Infrastructure (IaC, cloud config).
3. **Rate each practice** — for each activity (e.g., "Use of multiple SAST tools", "SAST integrated into developer IDE"), select your current level (0–4) based on evidence.
4. **Export the gap report** — DSOMM generates a heatmap of current state vs. target level, and a list of gap activities with references to tools and implementation steps.
5. **Create backlog items** — for each gap, create a ticket. DSOMM links each practice to implementation guidance.
6. **Re-assess quarterly** — re-run the assessment and compare to the previous export. The delta is the evidence of progress.

## From benchmark to roadmap

Benchmarks are most valuable when they feed planning:

1. Run the benchmark and record scores per domain/check.
2. Identify the lowest-scoring areas with the highest risk impact.
3. Create prioritized backlog items with owners and remediation timelines.
4. Re-run on a defined cadence and track delta.
5. Report trend to leadership quarterly.

Link each benchmark gap back to the framework it addresses — a failing Scorecard "Pinned-Dependencies" check maps to SLSA Supply Chain Threats and OWASP Top 10 CI/CD Risk #8. This cross-referencing is what turns a benchmark score into a compliance argument (see [Compliance Auditing](3-1-1-Compliance-Auditing.md)).

## Maturity progression

**Starter** — CIS Benchmarks run manually on a sample of systems before a major audit. Scorecard run once on critical repos. No automated tracking.

**Intermediate** — kube-bench running as a scheduled CronJob; Prowler scanning cloud accounts weekly. Scorecard in CI for all repositories. Gaps tracked as backlog items. SAMM or DSOMM assessment conducted annually.

**Advanced** — all benchmark checks automated and continuous. Scores feed a centralized dashboard alongside scan findings. Drift from baseline triggers an alert. Maturity assessments are quarterly, with a formal roadmap reviewed by security leadership. CIS scores part of deployment gates for new environment provisioning.

## Common pitfalls

- **Checkbox compliance** — reaching a benchmark score by disabling checks or documenting exceptions without fixing the underlying issue. Track the exclusion list as carefully as the score; unexplained gaps attract auditor scrutiny.
- **Benchmarking only at audit time** — a configuration that passes a benchmark on Monday can drift by Friday. Continuous checks are the only reliable approach.
- **Ignoring model intent** — SAMM and DSOMM describe practices to *do*, not just policies to *have*. An organization that documents a threat modeling process but runs no threat models scores artificially high.
- **Comparing incomparable scores** — Scorecard v3 and v4 scores are not directly comparable. BSIMM data changes as the participating firms evolve. Always version your benchmark runs and note the benchmark version in reporting.

## Metrics

| Metric | What it tells you |
|---|---|
| CIS Benchmark score (% passing) | Configuration hardening level by system/environment |
| OpenSSF Scorecard score (by repo) | Supply-chain security health of repositories |
| SAMM/DSOMM maturity level by practice | Where the program is strong and where it lags |
| Number of benchmark checks with accepted exclusions | Residual risk from environment-specific gaps |
| Score delta quarter-over-quarter | Whether the program is improving |

---

## Tools[^1]

### Open-source

- [kube-bench](https://github.com/aquasecurity/kube-bench) — checks Kubernetes nodes and control plane against the CIS Kubernetes Benchmark. Can run as a Job in-cluster or as a standalone binary. The de facto standard for Kubernetes CIS compliance.
- [OpenSCAP](https://www.open-scap.org/) — scans Linux systems against SCAP/XCCDF baselines including CIS Benchmarks and DISA STIGs. Produces XML and HTML reports; integrates with Satellite and Ansible for remediation.
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) — scores repositories on 20+ supply-chain security checks. Run via GitHub Actions or as a CLI; results can be published to the OpenSSF dashboard.
- [Prowler](https://github.com/prowler-cloud/prowler) — cloud security posture assessment for AWS, Azure, and GCP. Covers CIS Foundations Benchmarks, PCI DSS, HIPAA, GDPR, and more. Strong CLI and CI integration.

### Commercial

- [CIS-CAT Pro](https://www.cisecurity.org/cybersecurity-tools/cis-cat-pro) — automated assessment against CIS Benchmarks with multi-system scanning, remediation guidance, and report generation. The official CIS tool; useful for large-scale OS and server compliance programs.

---

### Links

[^1]: Listed in alphabetical order.
