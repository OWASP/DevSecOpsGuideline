# Misconfiguration Check

Security misconfiguration is one of the most common — and most preventable — causes of breaches. It is consistently in the [OWASP Top 10](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/). Unlike code vulnerabilities, misconfigurations arise from *how systems are set up*: default credentials left in place, unnecessary features enabled, verbose errors, missing hardening, and overly permissive access. Misconfiguration checks systematically verify that applications, infrastructure, containers, and cloud resources are configured against secure baselines.

## Why misconfigurations dominate breaches

Misconfigurations are exploitable with little skill — no custom exploit is needed. A public S3 bucket, an exposed Kubernetes dashboard, or a management port open to the internet can be found and exploited within hours of deployment. The combination of complexity (modern infrastructure has thousands of configuration parameters), speed (infrastructure is provisioned and changed continuously), and default-insecure tooling makes misconfiguration a persistent, high-probability risk that requires automated, continuous checking rather than periodic audits.

## Common misconfigurations by layer

### Application and web server
- Missing security headers: `Content-Security-Policy`, `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options`, `Permissions-Policy`.
- Insecure TLS: TLS 1.0/1.1 still enabled, weak cipher suites, missing HSTS, missing certificate pinning.
- Verbose error messages leaking stack traces, internal paths, or framework versions.
- Debug endpoints (`/actuator`, `/_debug`, `/graphiql`) left enabled in production.
- Default or sample accounts not removed.

### Infrastructure as Code
- Open-to-internet security groups (`0.0.0.0/0` on port 22 or 3389).
- Storage buckets with public read/write ACLs.
- Unencrypted EBS volumes, RDS databases, or S3 buckets.
- Missing resource-level IAM conditions (e.g., `aws:RequestedRegion`).

These are best caught before provisioning — see [IaC Scanning](../2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md).

### Containers and Kubernetes
- Containers running as root with no `runAsNonRoot: true` pod spec.
- Privileged containers (`privileged: true`) or excessive capabilities (`CAP_SYS_ADMIN`).
- Missing resource limits (CPU/memory) creating DoS risk.
- No network policies — all pods can communicate with all pods by default.
- No Pod Security Standards (PSS) admission control enforced at the cluster level.
- Public-facing Kubernetes dashboard with weak or no authentication.

### Cloud (runtime posture)
- IAM users with full `*:*` permissions or stale access keys (>90 days without rotation).
- Root account MFA not enabled.
- CloudTrail/audit logging disabled for critical APIs.
- Security group rules accumulated over time, never reviewed.
- No encryption at rest for databases and object storage.

## How to check, across layers

- **Application and web server** — verify headers, TLS configuration, error handling, and disabled debug features; often done via [DAST](2-4-2-Dynamic-Application-Security-Testing.md) or dedicated header-check tools in CI.
- **Infrastructure as Code** — catch misconfigurations before provisioning with Trivy, Checkov, or tfsec (see [IaC Scanning](../2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md)).
- **Containers and Kubernetes** — check images and cluster configuration against [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks) and Pod Security Standards using kube-bench, Trivy, or Kubescape.
- **Cloud resources at runtime** — Cloud Security Posture Management (CSPM) and Kubernetes Security Posture Management (KSPM) detect drift and misconfigurations in live environments continuously (see [Cloud-Native Security](../2-7-Operate/2-7-1-Cloud-Native-Security.md)).

## CI/CD integration example (Trivy misconfiguration scan)

```yaml
# GitHub Actions — scan IaC and Kubernetes manifests
- name: Trivy misconfiguration scan
  uses: aquasecurity/trivy-action@master
  with:
    scan-type: config
    scan-ref: .
    severity: HIGH,CRITICAL
    exit-code: 1
    format: sarif
    output: trivy-misconfig.sarif

- name: Upload results to GitHub Security
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-misconfig.sarif
```

## Make it continuous

Configuration drifts over time, so a one-time check is insufficient. A configuration that passes today can be manually changed tomorrow, overridden by a Helm upgrade, or exposed by a new feature. Define secure baselines as [Policy as Code](../../3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md), enforce them in CI and at admission control (Kyverno, OPA/Gatekeeper), and continuously monitor running environments for drift with CSPM. Map checks to recognized benchmarks (CIS, NIST) so results are auditable and comparable over time.

## Common pitfalls and anti-patterns

- **One-time hardening with no drift detection** — a system hardened at launch drifts back to insecure state within months. Continuous monitoring is mandatory.
- **Treating IaC scanning as a replacement for runtime CSPM** — IaC misses manually applied changes, console-provisioned resources, and drift introduced between deploys.
- **Suppressing too many findings** — teams under pressure suppress "accepted" misconfigurations and never revisit them. Time-box all suppressions.
- **Ignoring informational and low findings** — missing security headers are "low severity" but exploited in real attacks (clickjacking, MIME sniffing). Build a remediation SLA for all severity levels.
- **Not mapping to a benchmark** — ad-hoc checklists drift over time and cannot be compared across teams. Use CIS Benchmarks or similar as the authoritative baseline.

## Maturity progression

**Starter** — Run Trivy `--scanners misconfig` in CI on IaC/Kubernetes manifests. Run kube-bench on all Kubernetes clusters. Fix high/critical findings before release.

**Intermediate** — Enforce IaC misconfiguration gate in CI (block on critical). Deploy CSPM tool (Prowler or cloud-native) for continuous runtime posture. Define secure configuration baselines per environment tier.

**Advanced** — Policy-as-code admission control (Kyverno/OPA) blocks misconfigured workloads at deploy time. CSPM alerts feed into SIEM with auto-remediation for common patterns (e.g., Lambda auto-closes public S3 ACLs). Track CIS Benchmark compliance score per environment as a KPI. Configuration drift triggers automated incident.

## Metrics and KPIs

- **CIS Benchmark compliance score (%)** per environment (dev/staging/prod) — track trend.
- **High/critical misconfiguration count** — by layer (app, IaC, container, cloud); should trend toward zero.
- **Mean time to remediate misconfigurations** — by severity tier.
- **Configuration drift incidents** — number of times runtime config diverged from IaC definition.
- **Suppressed finding count and age** — old suppressions indicate accepted-risk debt accumulating.

---

## Tools[^1]

### Open-source

- [kube-bench](https://github.com/aquasecurity/kube-bench) — Checks Kubernetes nodes and control plane against the CIS Benchmark; run as a Job in-cluster for comprehensive coverage.
- [Kubescape](https://github.com/kubescape/kubescape) — Kubernetes security posture tool covering NSA/CISA hardening guidance, MITRE ATT&CK, and CIS Benchmarks; developer-friendly CLI and CI integration.
- [Lynis](https://github.com/CISOfy/lynis) — Security auditing and hardening tool for Unix/Linux systems; covers system configuration, package management, authentication, and more.
- [Prowler](https://github.com/prowler-cloud/prowler) — Cloud security posture and misconfiguration assessment for AWS, Azure, and GCP; maps to CIS, SOC2, PCI-DSS, ISO 27001, and HIPAA.
- [Trivy](https://github.com/aquasecurity/trivy) — Misconfiguration scanning for IaC (Terraform, CloudFormation, Helm, Kubernetes manifests); also covers container images and dependencies in a single tool.

### Commercial

- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud) — CNAPP with cloud posture management, IaC scanning, and runtime misconfiguration detection; strong cross-cloud coverage.
- [Wiz](https://www.wiz.io/) — Agentless cloud misconfiguration and posture management; fast deployment with graph-based risk prioritization that connects misconfigurations to their blast radius.

---

### Links

[^1]: Listed in alphabetical order.
