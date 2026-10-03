# Policy as Code

Policy as Code (PaC) expresses security, compliance, and operational rules as **machine-readable, version-controlled code** that is automatically evaluated and enforced — rather than as documents humans are expected to remember and follow. This makes policy consistent, testable, auditable, and impossible to silently skip, which is exactly what a high-velocity DevSecOps pipeline needs.

## Why policy as code

- **Consistency** — the same rule is enforced identically everywhere, every time, without relying on individual judgment or memory.
- **Automation** — policies run in CI and at admission without manual gatekeeping or review bottlenecks.
- **Version control and review** — policy changes go through pull requests with history, diff, and accountability. Rolling back a bad policy is a revert.
- **Testability** — policies can be unit-tested against example inputs before rollout, preventing both false positives and missed cases.
- **Auditability** — every decision is logged with the input, the policy version, and the outcome — producing structured evidence for [Compliance Auditing](3-1-1-Compliance-Auditing.md).
- **Scalability** — one centrally maintained policy library can be distributed to thousands of pipelines, services, and clusters simultaneously.

## Where policy as code is applied

- **CI/CD gates** — block merges or builds that violate policy (e.g., "no critical vulnerabilities", "SBOM required", "image must be signed"). Conftest tests structured config files (Kubernetes manifests, Terraform plans, Helm values) against Rego policies before they are applied.
- **Admission control** — Kubernetes admission controllers (OPA Gatekeeper, Kyverno) reject non-compliant or unsigned workloads at the point of deploy (see [Deploy](../../2-Process/2-6-Deploy/2-6-1-Deploy.md)).
- **Infrastructure as Code** — enforce guardrails on Terraform/Kubernetes before provisioning (see [IaC Scanning](../../2-Process/2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md)).
- **Cloud guardrails** — preventive controls (Service Control Policies in AWS, Azure Policy, GCP Organization Policy) prevent forbidden actions from being performed at all.
- **API authorization** — OPA is commonly used as an external authorization engine to evaluate fine-grained access-control policies separately from application code.

## Policy examples

### Block `:latest` image tags

```rego
# deny_latest_tag.rego
package main

deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  endswith(container.image, ":latest")
  msg := sprintf("Container '%v' must not use the :latest tag — pin to a digest or versioned tag", [container.name])
}
```

### Require `runAsNonRoot`

```rego
# require_non_root.rego
package main

deny[msg] {
  input.kind == "Deployment"
  container := input.spec.template.spec.containers[_]
  not container.securityContext.runAsNonRoot
  msg := sprintf("Container '%v' must set securityContext.runAsNonRoot: true", [container.name])
}
```

### Require required labels

```rego
# require_labels.rego
package main

required_labels := {"app", "team", "env"}

deny[msg] {
  input.kind == "Deployment"
  label := required_labels[_]
  not input.metadata.labels[label]
  msg := sprintf("Deployment is missing required label: '%v'", [label])
}
```

### Block no-root enforcement missing from securityContext (Kyverno YAML alternative)

```yaml
# kyverno-require-non-root.yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-run-as-non-root
spec:
  validationFailureAction: enforce
  rules:
    - name: check-runAsNonRoot
      match:
        resources:
          kinds: ["Pod"]
      validate:
        message: "Containers must not run as root. Set runAsNonRoot: true in securityContext."
        pattern:
          spec:
            containers:
              - securityContext:
                  runAsNonRoot: true
```

## OPA integration in CI — step by step

1. **Install Conftest** in your CI image or as a binary download step:
   ```bash
   wget https://github.com/open-policy-agent/conftest/releases/download/v0.50.0/conftest_0.50.0_Linux_x86_64.tar.gz
   tar xzf conftest_*.tar.gz && mv conftest /usr/local/bin/
   ```

2. **Store policies** in a `policy/` directory in your repo (or reference a shared OCI bundle):
   ```
   policy/
     deny_latest_tag.rego
     require_non_root.rego
     require_labels.rego
   ```

3. **Run in CI** against generated Kubernetes manifests before applying:
   ```bash
   helm template my-app ./chart > rendered.yaml
   conftest test rendered.yaml --policy ./policy/
   ```

4. **Interpret results** — conftest exits non-zero if any `deny` rule fires. CI blocks the job and surfaces the message to the developer.

5. **Promote to enforcement** — once the policy has been running in warn mode for two sprints without significant false positives, remove the `--no-fail` flag so violations block the pipeline.

## Testing policies

A policy that is not tested is a policy that may silently fail. Use OPA's built-in test framework:

```rego
# deny_latest_tag_test.rego
package main

test_deny_latest {
  deny["Container 'app' must not use the :latest tag — pin to a digest or versioned tag"] with input as {
    "kind": "Deployment",
    "spec": {"template": {"spec": {"containers": [{"name": "app", "image": "myrepo/myimage:latest"}]}}}
  }
}

test_allow_pinned {
  count(deny) == 0 with input as {
    "kind": "Deployment",
    "spec": {"template": {"spec": {"containers": [{"name": "app", "image": "myrepo/myimage:sha256-abc123"}]}}}
  }
}
```

Run with: `opa test ./policy/`

Require 100% test coverage for all `deny` rules before promoting to enforcement mode.

## Policy library management

At scale, individual teams should consume policies — not author them. A platform team model:

- **Central policy repository** — all organizational policies live in a single, reviewed repo. Changes require at least two approvals.
- **OCI distribution** — package and publish policies as OCI artifacts to your container registry. Conftest can pull directly: `conftest pull oci://myregistry/policies:v1.2`.
- **Versioned releases** — tag policy releases. Pipelines pin to a specific version. Breaking policy changes are pre-announced and coordinated.
- **Policy changelog** — maintain a changelog. Teams need to understand what changed between policy versions and why, so they can prepare before upgrading.
- **Exemption process** — define how teams can request a policy exemption for a specific resource, with a named owner and expiry date. Exemptions are stored as OPA annotations or Kyverno exceptions, not as silently disabled checks.

## Good practice

- **Start with guardrails, not handcuffs** — begin in warn/audit mode, then move high-confidence rules to enforce after validating false-positive rates. This builds developer trust rather than creating immediate friction.
- **Codify organization-specific rules** — encode the policies unique to your risk appetite and regulatory context, not just generic benchmarks.
- **Provide clear, actionable messages** — when a policy blocks something, tell the developer exactly what to change and why. A cryptic OPA error kills adoption.
- **Unit-test every policy** — use OPA's built-in test framework or Kyverno's `test` command to validate that policies correctly allow and deny the right inputs before deploying them.
- **Gate policy changes like code changes** — a policy change that silently widens permissions is as dangerous as a code change that introduces a vulnerability.

## Maturity progression

**Starter** — a few ad-hoc Conftest or OPA checks run in CI for the most critical rules (e.g., no hardcoded secrets, no public buckets). Policies live in individual repos with no central coordination.

**Intermediate** — a centrally maintained policy library distributed to all pipelines. Kubernetes admission control enforced via Gatekeeper or Kyverno. Policies are version-controlled, reviewed, and unit-tested. Warn vs. enforce distinction managed deliberately.

**Advanced** — full policy lifecycle management via a platform like Styra DAS or a custom OPA bundle server. Every compliance control from [Compliance Auditing](3-1-1-Compliance-Auditing.md) has a corresponding policy check. Policy decisions are logged to SIEM for audit evidence. SLO on policy coverage: 100% of production workloads governed by at least one admission policy.

## Common pitfalls

- **Policies that are always in warn mode** — a policy that never enforces is theater. Build a path from warn to enforce for every rule with a defined timeline.
- **No tests for the policy itself** — untested policies silently fail to catch what they were meant to catch, discovered only after an incident.
- **Overly broad deny rules** — a policy that blocks too much gets disabled by teams under pressure. Tune aggressively on false positive rate before enforcing.
- **Policy debt** — policies accumulate without pruning. Stale rules that no longer apply create confusion and noise. Review the policy library quarterly.
- **No exemption process** — teams under deadline that cannot get an exemption will delete the policy check. A defined exemption path keeps the policy in place.

## Metrics

| Metric | What it tells you |
|---|---|
| % of pipelines with at least one enforcement-mode policy | Governance coverage across the estate |
| Policy violation rate by rule | Which policies are blocking most; candidates for tuning or developer education |
| Warn-to-enforce migration rate | Maturity of the policy program; stagnation in warn mode is a risk signal |
| Policy test coverage | How thoroughly policies are validated before rollout |
| Open policy exemptions by age | Exemptions that have not been closed indicate growing residual risk |

---

## Tools[^1]

### Open-source

- [Checkov](https://www.checkov.io/) — policy-as-code scanning for IaC (Terraform, CloudFormation, Kubernetes, Helm) with hundreds of built-in rules and support for custom Rego or Python policies. Integrates natively with most CI systems.
- [Conftest](https://www.conftest.dev/) — tests any structured configuration (YAML, JSON, HCL, Dockerfile, etc.) against Rego policies. Ideal for pre-deploy validation in CI without a running cluster.
- [Gatekeeper](https://github.com/open-policy-agent/gatekeeper) — OPA-based Kubernetes admission controller. Enforces policies at the Kubernetes API level, preventing non-compliant resources from ever being admitted. Supports audit mode for existing resources.
- [Kyverno](https://kyverno.io/) — Kubernetes-native policy engine using YAML-based policies (no Rego). Easier adoption for teams unfamiliar with Rego; supports mutating policies (auto-remediation) as well as validation.
- [Open Policy Agent (OPA)](https://www.openpolicyagent.org/) — general-purpose policy engine using the Rego language. The foundation for Conftest, Gatekeeper, and many other tools. Use directly for API authorization and custom enforcement contexts.

### Commercial

- [Styra DAS](https://www.styra.com/) — management plane for OPA policies at scale. Provides centralized authoring, testing, distribution, and decision logging for OPA across hundreds of services and clusters.

---

### Links

[^1]: Listed in alphabetical order.
