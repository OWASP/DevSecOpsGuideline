# Infrastructure as Code (IaC) Scanning

Infrastructure is now defined in code — Terraform, CloudFormation, Kubernetes manifests, Helm charts, Ansible, and more. That means infrastructure misconfigurations can be caught with the **same shift-left discipline as application code**: scanned statically, before anything is provisioned. IaC scanning finds insecure defaults and policy violations early, when they are a one-line fix rather than a production incident costing hours of remediation and potential data exposure.

## The Capital One breach: IaC misconfiguration at scale

In 2019, the Capital One breach exposed over 100 million customer records. The root cause was an overly permissive IAM role — a Server Side Request Forgery (SSRF) vulnerability allowed an attacker to query the EC2 metadata service, which returned temporary credentials for an IAM role with excessive S3 permissions. That IAM role configuration was defined in infrastructure code. Had IaC scanning with IAM privilege analysis been in place, the overpermissioned role would have been flagged before it was ever applied. The breach cost Capital One over $80 million in fines and settlement costs.

This is the canonical case for why IaC security cannot be treated as optional or post-deployment.

## What IaC scanning finds

- **Insecure cloud configuration** — public storage buckets (S3, GCS, Azure Blob), open security groups (0.0.0.0/0 ingress), unencrypted databases, overly permissive IAM policies and roles.
- **Kubernetes misconfigurations** — privileged pods, missing resource limits and requests, host mounts, weak or missing network policies, unenforced pod security standards.
- **Missing encryption and logging** — resources lacking encryption at rest or in transit; CloudTrail, VPC flow logs, or audit logging disabled.
- **Policy violations** — drift from organizational standards and compliance baselines (CIS, SOC 2, PCI-DSS, HIPAA).
- **Secrets in IaC** — hardcoded credentials, access keys, or passwords in Terraform variable files, Helm values, or Ansible vars.
- **Overprivileged network exposure** — databases reachable from the internet, internal services with public load balancers, unrestricted egress.

## Misconfiguration examples by IaC type

**Terraform (AWS):**
```hcl
# BAD: S3 bucket publicly accessible
resource "aws_s3_bucket_acl" "example" {
  bucket = aws_s3_bucket.example.id
  acl    = "public-read"           # flags CKV_AWS_20
}

# BAD: Security group open to world
resource "aws_security_group_rule" "bad" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]     # flags CKV_AWS_25
}

# GOOD: Restrict SSH to known CIDR
resource "aws_security_group_rule" "good" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]
}
```

**Kubernetes / Helm (running as root):**
```yaml
# BAD: Pod running as root
spec:
  containers:
  - name: app
    securityContext:
      runAsRoot: true              # flags KSV001

# GOOD: Non-root, read-only filesystem
spec:
  containers:
  - name: app
    securityContext:
      runAsNonRoot: true
      runAsUser: 1000
      readOnlyRootFilesystem: true
      allowPrivilegeEscalation: false
```

**CloudFormation (unrestricted ingress):**
```yaml
# BAD
SecurityGroupIngress:
  - IpProtocol: -1
    CidrIp: 0.0.0.0/0            # flags W2902

# GOOD
SecurityGroupIngress:
  - IpProtocol: tcp
    FromPort: 443
    ToPort: 443
    CidrIp: 10.0.0.0/8
```

## Where it fits

- **IDE and pre-commit** — instant feedback as infrastructure code is written; the cheapest possible fix point.
- **CI / pull request** — authoritative scan; gate merges on new high-severity misconfigurations. Infrastructure PRs carry the same risk as application PRs.
- **Pre-deploy** — final check before `terraform apply` or `kubectl apply`; combined with [Policy as Code](../../../3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md) to enforce guardrails at the cluster or cloud API level.

```yaml
# Example: Checkov scan in GitHub Actions
- name: Scan Terraform with Checkov
  uses: bridgecrewio/checkov-action@master
  with:
    directory: ./infra/terraform
    framework: terraform
    output_format: sarif
    output_file_path: checkov-results.sarif
    soft_fail: false
    check: CKV_AWS_*

- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: checkov-results.sarif
```

## Custom Checkov policies

Out-of-the-box rules cover common benchmarks, but organizations need custom rules for internal standards. Checkov supports Python-based custom checks:

```python
# custom_checks/check_rds_no_public_access.py
from checkov.common.models.enums import CheckCategories, CheckResult
from checkov.terraform.checks.resource.base_resource_check import BaseResourceCheck

class RDSNoPublicAccess(BaseResourceCheck):
    def __init__(self):
        name = "Ensure RDS instance is not publicly accessible"
        id = "CKV_CUSTOM_RDS_1"
        supported_resources = ["aws_db_instance"]
        categories = [CheckCategories.NETWORKING]
        super().__init__(name=name, id=id, categories=categories,
                         supported_resources=supported_resources)

    def scan_resource_conf(self, conf):
        publicly_accessible = conf.get("publicly_accessible", [False])
        if publicly_accessible == [True] or publicly_accessible is True:
            return CheckResult.FAILED
        return CheckResult.PASSED

scanner = RDSNoPublicAccess()
```

Run with: `checkov -d ./infra --external-checks-dir ./custom_checks`

## Shift-left IaC: IDE integration

IDE plugins bring IaC scanning to the point of authorship — the cheapest fix:
- **VS Code Checkov extension** — real-time inline highlighting of misconfigurations as Terraform or Kubernetes YAML is written. No CLI required.
- **Snyk IaC VS Code plugin** — live fix suggestions alongside detected issues.
- **IntelliJ + Terraform plugin** — structural validation before any CI run.

## Policy-as-code integration with OPA

For organization-specific policies beyond CIS benchmarks, use OPA/Conftest to evaluate IaC against custom Rego rules in CI:

```rego
# policies/terraform/no_public_s3.rego
package main

deny[msg] {
  resource := input.resource.aws_s3_bucket_acl[_]
  resource.acl == "public-read"
  msg := sprintf("S3 bucket ACL must not be public-read: %v", [resource])
}
```

```bash
# In CI: evaluate rendered Terraform plan against policies
terraform plan -out=plan.tfplan
terraform show -json plan.tfplan > plan.json
conftest test plan.json --policy policies/terraform/
```

## The drift detection gap

IaC scanning checks the *declared* state. Runtime configuration can drift from what was applied — a developer makes a manual change in the console, an automated process modifies a resource, or an incident response action is never codified. This gap requires runtime posture management ([CNAPP](../../2-7-Operate/2-7-1-Cloud-Native-Security.md)) to catch the *actual* state and feed drift findings back into the IaC. A finding in IaC scanning does not guarantee the issue exists in production; a clean IaC scan does not guarantee the cloud environment is clean.

## Scan Helm charts before installation

Helm templates are rendered to Kubernetes manifests at deploy time. Scanning the raw templates misses values-substitution — a production `values.yaml` might override safe defaults with insecure ones. Always scan the rendered output:

```bash
helm template myapp ./chart -f prod-values.yaml | trivy config -
helm template myapp ./chart -f prod-values.yaml | checkov -f /dev/stdin --framework kubernetes
```

## Common pitfalls and anti-patterns

- **Suppressing findings by rule ID without documented justification** — suppression files accumulate silently. Require justification and owner for every suppression.
- **Scanning only Terraform, not Helm or CloudFormation** — multi-tool environments require multi-language IaC scanning.
- **No link between IaC findings and runtime posture** — a bucket flagged in IaC as "not public" may have been manually made public in the console. Without runtime CSPM, the IaC scan gives false assurance.
- **Policy-as-code rules that are too broad** — rules like "no security group with any port open" that fire for legitimate HTTPS traffic cause developers to disable the scanner.
- **Treating IaC scanning as purely a security responsibility** — platform engineers who write IaC should own the findings, just as developers own SAST results.
- **No baseline management** — gating on all existing findings on day one creates an unmergeable backlog. Gate on *new* findings first; reduce existing debt on a planned schedule.

## Maturity progression

**Starter** — Run Checkov or KICS in CI against all Terraform and Kubernetes manifests. Report findings. Establish a baseline of existing issues. Block the pipeline on new critical findings.

**Intermediate** — Integrate scanning into IDE (VS Code Checkov extension, Snyk IaC). Map findings to CIS benchmarks and compliance frameworks. Add Helm chart scanning (rendered output). Enforce policy-as-code rules for the top 10 organization-specific constraints.

**Advanced** — Implement full policy-as-code enforcement (OPA/Conftest in CI + Kyverno/OPA Gatekeeper in Kubernetes admission). Track and measure drift between declared IaC state and actual runtime state via CNAPP integration. Feed CSPM findings back into IaC as automated PRs. Align all IaC policies to SOC 2 / PCI controls and generate continuous compliance evidence.

## Metrics and KPIs

| Metric | Target |
|---|---|
| IaC PRs merged with new high/critical misconfigurations | 0 |
| Suppressed findings without documented justification | 0 |
| % of IaC surface area covered by scanning | 100% |
| Drift findings (runtime vs declared state) | Decreasing month-over-month |
| Mean time to remediate IaC critical findings | < 5 business days |
| Custom policies covering top internal standards | Tracked; gap analysis reviewed quarterly |

---

## Tools[^1]

### Open-source

- [Checkov](https://www.checkov.io/) — Static analysis for Terraform, CloudFormation, Kubernetes, Helm, Bicep, and ARM; 1000+ built-in policies; supports custom Python and OPA rules, SARIF output. Best breadth for multi-IaC environments.
- [KICS](https://kics.io/) — Finds security vulnerabilities and misconfigurations in IaC; supports 24 IaC platforms; built-in compliance framework mappings. Strong for teams that need framework-aligned reporting (PCI, HIPAA).
- [Kubescape](https://github.com/kubescape/kubescape) — Kubernetes security scanning against NSA/CISA hardening guidance and MITRE ATT&CK; scans live clusters and IaC before apply. Best Kubernetes-specific coverage.
- [Terrascan](https://github.com/tenable/terrascan) — Detects compliance and security violations across Terraform, Kubernetes, Helm, and Dockerfiles; integrates with Argo CD for GitOps security.
- [Trivy](https://github.com/aquasecurity/trivy) — Scans IaC and configuration alongside CVE scanning; good choice for teams already using Trivy for container scanning who want one tool.

### Commercial

- [Prisma Cloud (IaC Security)](https://www.paloaltonetworks.com/prisma/cloud) — IaC scanning within a full CNAPP platform; strong compliance framework coverage and cloud-runtime correlation. Best for organizations also using Prisma for cloud posture management.
- [Snyk IaC](https://snyk.io/product/infrastructure-as-code-security/) — Developer-first IaC misconfiguration scanning with IDE plugins, PR checks, and fix guidance; fastest developer adoption curve.

---

### Links

[^1]: Listed in alphabetical order.
