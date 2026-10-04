# Infrastructure as Code (IaC) Scanning

Infrastructure is now defined in code — Terraform, CloudFormation, Kubernetes manifests, Helm charts, Ansible, and more. That means infrastructure misconfigurations can be caught with the **same shift-left discipline as application code**: scanned statically, before anything is provisioned. IaC scanning finds insecure defaults and policy violations early, when they are a one-line fix rather than a production incident costing hours of remediation and potential data exposure.

## The Capital One breach: IaC misconfiguration at scale

In 2019, the Capital One breach exposed the personal data of over 100 million customers. An attacker exploited a misconfigured web application firewall to perform a Server Side Request Forgery (SSRF) attack against the EC2 metadata service, which returned temporary credentials for an IAM role with far broader S3 access than the workload needed. The misconfiguration was a cloud-configuration failure rather than a proven IaC defect, but it is exactly the class of issue — over-permissive IAM roles, exposed metadata service (IMDSv1), excessive data-store access — that IaC scanning and policy-as-code are designed to catch before anything is applied. The OCC fined Capital One $80 million, and the company later agreed to a $190 million class-action settlement.

This is the canonical case for why cloud configuration security cannot be treated as optional or post-deployment.

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
  cidr_blocks = ["0.0.0.0/0"]     # flags CKV_AWS_24
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
      runAsNonRoot: false          # flags KSV012 (runs as root); privileged: true would add KSV017

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
    CidrIp: 0.0.0.0/0            # flags cfn_nag W2 / W40 and Checkov CKV_AWS_24 (with SSH/RDP ports)

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
  uses: bridgecrewio/checkov-action@v12
  with:
    directory: ./infra/terraform
    framework: terraform
    output_format: sarif
    output_file_path: checkov-results.sarif
    soft_fail: false

- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v4
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
# Evaluates the JSON form of a Terraform plan (`terraform show -json`)
package main

import rego.v1

deny contains msg if {
  some rc in input.resource_changes
  rc.type == "aws_s3_bucket_acl"
  rc.change.after.acl == "public-read"
  msg := sprintf("S3 bucket ACL must not be public-read: %v", [rc.address])
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
helm template myapp ./chart -f prod-values.yaml --output-dir ./rendered
trivy config ./rendered
checkov -d ./rendered --framework kubernetes
```

## Common pitfalls and anti-patterns

- **Suppressing findings by rule ID without documented justification** — suppression files accumulate silently. Require justification and owner for every suppression.
- **Scanning only Terraform, not Helm or CloudFormation** — multi-tool environments require multi-language IaC scanning.
- **No link between IaC findings and runtime posture** — a bucket flagged in IaC as "not public" may have been manually made public in the console. Without runtime CSPM, the IaC scan gives false assurance.
- **Policy-as-code rules that are too broad** — rules like "no security group with any port open" that fire for legitimate HTTPS traffic cause developers to disable the scanner.
- **Treating IaC scanning as purely a security responsibility** — platform engineers who write IaC should own the findings, just as developers own SAST results.
- **No baseline management** — gating on all existing findings on day one creates an unmergeable backlog. Gate on *new* findings first; reduce existing debt on a planned schedule.

## Maturity progression

**Starter** — Run Checkov, KICS, or Trivy in CI against all Terraform (or OpenTofu) and Kubernetes manifests. Report findings. Establish a baseline of existing issues. Block the pipeline on new critical findings.

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
- [KICS](https://kics.io/) — Finds security vulnerabilities and misconfigurations in IaC; supports 20+ IaC platforms; built-in compliance framework mappings. Strong for teams that need framework-aligned reporting (PCI, HIPAA).
- [Kubescape](https://github.com/kubescape/kubescape) — Kubernetes security scanning against NSA/CISA hardening guidance and MITRE ATT&CK; scans live clusters and IaC before apply. Best Kubernetes-specific coverage.
- [OPA / Conftest](https://www.conftest.dev/) — Evaluates Terraform plans, Kubernetes manifests, and other structured config against custom Rego policies in CI; the usual choice for organization-specific rules.
- [Trivy](https://github.com/aquasecurity/trivy) — Scans IaC and configuration alongside CVE scanning (it absorbed the former tfsec project); good choice for teams already using Trivy for container scanning who want one tool. Pin the binary and its GitHub Action to verified releases (see [Container Scanning](../2-3-3-Container-Security/2-3-3-1-Container-Scanning.md)).

> **Retired tools:** Terrascan (Tenable) was archived in November 2025 and tfsec has been folded into Trivy; migrate existing pipelines to Checkov, KICS, or Trivy.

### Commercial

- [Prisma Cloud (IaC Security)](https://www.paloaltonetworks.com/prisma/cloud) — IaC scanning within a full CNAPP platform; strong compliance framework coverage and cloud-runtime correlation. Best for organizations also using Prisma for cloud posture management.
- [Snyk IaC](https://snyk.io/product/infrastructure-as-code-security/) — Developer-first IaC misconfiguration scanning with IDE plugins, PR checks, and fix guidance; fastest developer adoption curve.

---

### Links

[^1]: Listed in alphabetical order.
