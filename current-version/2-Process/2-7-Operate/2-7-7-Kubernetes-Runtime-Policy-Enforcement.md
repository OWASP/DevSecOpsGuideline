# Kubernetes Runtime Policy Enforcement

Scanning manifests and images in the pipeline tells you what *should* be deployed; it does not stop someone from applying a privileged pod with `kubectl`, from a compromised controller creating one, or from a running container being abused. **Runtime policy enforcement** puts guardrails at the cluster itself, at three points: **admission** (what is allowed to be created), **network** (what is allowed to talk), and **kernel/runtime** (what a running workload is allowed to do). Together they turn the standards you defined in [Cloud-Native Security](2-7-1-Cloud-Native-Security.md) and the checks you run in [Deploy](../2-6-Deploy/2-6-1-Deploy.md) into controls that hold even when the pipeline is bypassed.

## Layer 1: Admission control

### Pod Security Admission (built in)

Pod Security Admission (PSA) enforces the [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) — `privileged`, `baseline`, and `restricted` — per namespace through labels. It is the lowest-effort control and should be the default everywhere:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: payments
  labels:
    pod-security.kubernetes.io/enforce: baseline
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

This blocks baseline violations while reporting (without blocking) what would fail under `restricted`, giving teams a migration path.

### ValidatingAdmissionPolicy (built in, CEL)

[ValidatingAdmissionPolicy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) is stable since Kubernetes 1.30 and evaluates [CEL](https://kubernetes.io/docs/reference/using-api/cel/) expressions inside the API server — no webhook to run or keep available. A policy needs a binding, and the binding's `validationActions` control the rollout:

```yaml
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicy
metadata:
  name: require-resource-limits
spec:
  failurePolicy: Fail
  matchConstraints:
    resourceRules:
      - apiGroups: ["apps"]
        apiVersions: ["v1"]
        operations: ["CREATE", "UPDATE"]
        resources: ["deployments"]
  validations:
    - expression: "object.spec.template.spec.containers.all(c, has(c.resources.limits) && has(c.resources.limits.memory))"
      message: "All containers must set memory limits."
---
apiVersion: admissionregistration.k8s.io/v1
kind: ValidatingAdmissionPolicyBinding
metadata:
  name: require-resource-limits
spec:
  policyName: require-resource-limits
  validationActions: [Warn, Audit]   # switch to [Deny] after violations reach zero
  matchResources:
    namespaceSelector:
      matchLabels:
        environment: production
```

### Policy engines: Kyverno and OPA Gatekeeper

Use a policy engine when you need more than the built-ins: mutation, generating resources, cross-resource lookups, image verification, reporting, and managed exceptions.

- **[Kyverno](https://kyverno.io/)** — policies are Kubernetes YAML (no new language), with validate, mutate, generate, and `verifyImages` rules, policy reports, and `PolicyException` resources for sanctioned exceptions.
- **[OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)** — policies are written in Rego as `ConstraintTemplate` plus `Constraint` objects; strong when you already use OPA elsewhere (Terraform, APIs) and want one policy language, and it supports an `enforcementAction` of `dryrun`, `warn`, or `deny`.

Both can complement the built-in policies; pick one engine as the standard rather than running several overlapping sets.

### Verify images at admission

Signing in CI only matters if the cluster checks it. Require that images come from approved registries and carry a valid signature or attestation (see [Container Scanning](../2-3-Build/2-3-3-Container-Security/2-3-3-1-Container-Scanning.md) and [SBOM](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md)):

```yaml
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  rules:
    - name: check-signature
      match:
        any:
          - resources:
              kinds: [Pod]
      verifyImages:
        - imageReferences: ["registry.example.com/myorg/*"]
          failureAction: Audit          # change to Enforce once signing coverage is complete
          mutateDigest: true            # pin tags to verified digests
          attestors:
            - entries:
                - keyless:
                    issuer: https://token.actions.githubusercontent.com
                    subject: https://github.com/myorg/*
```

Field names vary between Kyverno releases; check the documentation for the version you run. Sigstore's [policy-controller](https://github.com/sigstore/policy-controller) is an alternative focused on signature verification.

## Layer 2: Network policy

Start every namespace with default-deny ingress and egress (see the example in [Cloud-Native Security](2-7-1-Cloud-Native-Security.md)), then allow only required flows, including DNS egress. NetworkPolicy is only enforced if your CNI supports it (for example Cilium or Calico), so test enforcement explicitly. Use the CNI's flow logs (such as Hubble for Cilium) to learn real traffic before tightening. Add admission policies requiring a NetworkPolicy per namespace to prevent drift.

## Layer 3: Runtime enforcement in the kernel

Admission decides what may start; runtime tools constrain what it may *do* afterwards:

- **Detect** — [Falco](https://falco.org/) alerts on suspicious syscalls and behavior; pair it with response automation.
- **Enforce** — [Tetragon](https://github.com/cilium/tetragon) (eBPF) can block or kill on policy match, and [KubeArmor](https://github.com/kubearmor/KubeArmor) enforces process, file, and network restrictions using Linux security modules (AppArmor, SELinux, BPF-LSM):

```yaml
apiVersion: security.kubearmor.com/v1
kind: KubeArmorPolicy
metadata:
  name: block-shells
  namespace: payments
spec:
  selector:
    matchLabels:
      app: api
  process:
    matchPaths:
      - path: /bin/sh
      - path: /bin/bash
  action: Block
```

- **Reduce the kernel attack surface** — set `seccompProfile: RuntimeDefault`, drop all capabilities, run as non-root with a read-only root filesystem (enforced via PSA `restricted`), and consider sandboxed runtimes such as gVisor or Kata Containers for untrusted workloads.

## Rolling out: audit, then enforce

1. **Inventory** — run policies in `audit`/`warn`/`dryrun` mode and collect violations per namespace and team.
2. **Fix or except** — remediate violations in the manifests; record the rest as time-boxed, owned exceptions.
3. **Enforce by scope** — enable deny in new namespaces and dev/staging first, then production, one policy at a time.
4. **Keep it enforced** — policies live in Git, are tested in CI against sample manifests (`kyverno test`, `gator test`, or `kubectl apply --dry-run=server`), and are deployed by GitOps.
5. **Manage exceptions** — exceptions are code-reviewed resources with an owner and expiry, never namespace-wide disables. Exempt system namespaces deliberately and narrowly.
6. **Mind failure modes** — webhook-based engines sit in the API request path; run replicas, set sensible `failurePolicy` and timeouts, and keep a break-glass procedure.

## Common pitfalls and anti-patterns

- **Enforce on day one** — blocking policies applied to a live cluster break deployments and teach teams to demand blanket exemptions. Audit first.
- **Permanent, unreviewed exceptions** — an exception list that only grows becomes the real policy. Require owner and expiry.
- **Policy sprawl across engines** — PSA, VAP, Kyverno, and Gatekeeper all enforcing different versions of the same rule makes outcomes hard to predict.
- **Admission only** — admission checks run at create/update time; they do not protect an already-running compromised container. Add network and runtime controls.
- **Assuming NetworkPolicy is enforced** — without a supporting CNI the objects are silently ignored.
- **Unverified exemptions for the policy engine itself** — excluding `kube-system` or the engine's own namespace broadly can leave a bypass path; scope exclusions tightly.
- **Detect-only runtime tooling nobody watches** — alerts need a routed response, or enforcement mode for the highest-confidence rules.

## Maturity progression

**Starter** — PSA labels on all namespaces (`baseline` enforce, `restricted` warn/audit). Default-deny NetworkPolicy in new namespaces. Image registry allow-list in audit mode.

**Intermediate** — Policy engine (Kyverno or Gatekeeper) with a policy library in Git, tested in CI. `restricted` enforced for application namespaces. Image signature verification in enforce mode for production. Exceptions tracked with owners and expiry. Falco alerts routed to the SIEM.

**Advanced** — Kernel-level enforcement (Tetragon or KubeArmor) for high-confidence behaviors, per-workload profiles generated from observed behavior. Sandboxed runtimes for untrusted workloads. Automated policy-violation reporting per team. Regular attack simulation (see [Breach and Attack Simulation](2-7-6-Breach-and-attack-simulation.md)) validates that policies actually block.

## Metrics and KPIs

- **Namespaces enforcing Pod Security `restricted`/`baseline`** — percentage of namespaces by level.
- **Policy violations by severity and age** — open audit-mode violations, trending toward zero before enforcement.
- **Active exceptions** — count, average age, and percentage past expiry.
- **Admission deny rate and break-glass use** — blocked deployments and emergency bypasses per month.
- **Network policy coverage** — percentage of namespaces with default-deny.
- **Signed-image coverage** — percentage of running workloads whose images pass verification.

---

## Tools[^1]

### Open-source

- [Cilium](https://cilium.io/) — eBPF-based CNI with L3/L4/L7 network policy and Hubble flow visibility.
- [Falco](https://falco.org/) — CNCF graduated runtime threat detection with a large community rule set.
- [KubeArmor](https://github.com/kubearmor/KubeArmor) — Runtime enforcement of process, file, and network restrictions on pods and nodes via Linux security modules (CNCF sandbox project).
- [Kyverno](https://kyverno.io/) — Kubernetes-native policy engine for validation, mutation, generation, image verification, and policy exceptions.
- [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/) — Rego-based admission controller with constraint templates, audit, and dry-run enforcement actions.
- [policy-controller (Sigstore)](https://github.com/sigstore/policy-controller) — Admission controller that verifies image signatures and attestations.
- [Tetragon](https://github.com/cilium/tetragon) — eBPF security observability and in-kernel runtime enforcement from the Cilium project.

### Commercial

- [Aqua Security](https://www.aquasec.com/) — Runtime protection and admission control built on the Aqua/Tracee eBPF stack.
- [Nirmata](https://nirmata.com/) — Enterprise policy management built around Kyverno.
- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud) — Admission control, runtime defense, and compliance for Kubernetes within a CNAPP.
- [Sysdig Secure](https://sysdig.com/products/secure/) — Falco-based runtime security with managed policies and response actions.

---

### Links

- [Kubernetes: Pod Security Admission](https://kubernetes.io/docs/concepts/security/pod-security-admission/)
- [Kubernetes: Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)
- [Kubernetes: Network Policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/)

[^1]: Listed in alphabetical order.
