# Deploy

Deployment moves a released artifact into a running environment. It is the last gate before software is exposed to real traffic, and it is where supply-chain verification, environment configuration, and runtime access converge. Secure deployment ensures that **only verified artifacts** reach production, that they run with **least privilege**, and that the blast radius of any problem is contained.

## Verify before you run: admission control

The deploy stage is where signing and provenance pay off. Do not allow an artifact to run unless you can cryptographically verify where it came from and that it passed required checks. Enforce policy at admission so that:

- Only **signed** artifacts with valid signatures are admitted (see [Artifact Signing and Provenance](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md)).
- Only artifacts with acceptable **provenance** (SLSA level, build workflow, source repository) run in production.
- Images that fail policy — unsigned, from untrusted registries, or containing unresolved critical CVEs — are **blocked at admission**, not merely flagged in a dashboard.

Kubernetes admission controllers (Kyverno, OPA/Gatekeeper, Sigstore policy-controller) enforce these rules as code, consistently and automatically.

```yaml
# Kyverno policy: require all images to be signed with cosign
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-image-signature
spec:
  validationFailureAction: Enforce
  rules:
    - name: check-image-signature
      match:
        resources:
          kinds: [Pod]
      verifyImages:
        - imageReferences: ["myregistry.io/*"]
          attestors:
            - entries:
                - keyless:
                    subject: "https://github.com/myorg/*"
                    issuer: "https://token.actions.githubusercontent.com"
```

## GitOps and declarative deployment

GitOps makes the desired state of an environment a version-controlled, auditable artifact:

- The git repository is the single source of truth for deployment state. Changes go through reviewed pull requests — not SSH sessions, not manual Helm installs.
- A reconciler (Argo CD, Flux) continuously applies the desired state and corrects drift. If someone manually modifies a running workload, the reconciler reverts it.
- Every change has a full audit trail: who opened the PR, who approved it, when it merged, what the diff was — all in git history.
- Rollback is a `git revert` — fast, auditable, and not dependent on tribal knowledge.

Use **image digest pinning** in deployment manifests rather than mutable tags:
```yaml
# Prefer this (immutable):
image: myregistry.io/myapp@sha256:a1b2c3d4...
# Not this (mutable):
image: myregistry.io/myapp:latest
```

## Limit blast radius with progressive delivery

Roll out changes gradually so a bad release — whether a bug, a security regression, or a compromised artifact — affects as few users and systems as possible:

- **Canary deployment** — route a small percentage of traffic (e.g., 5%) to the new version. Monitor error rates, latency, and security signals. Promote only if metrics are healthy.
- **Blue-green deployment** — run the new version alongside the old. Instantly switch traffic back if issues appear; the old version is not terminated until confidence is established.
- **Feature flags** — deploy code without activating new behavior; enable features for specific users or percentages via a feature flag service. Decouples deploy from release.
- **Automated rollback** — define health criteria and automatically revert if they breach thresholds within a deployment window.

## Least privilege and secrets at deploy

### Deploy identity

The service account or role used by the deployment pipeline should have:
- Write access only to the target environment (not all environments).
- Permission to update the specific workloads it manages, not cluster-admin.
- Time-limited credentials: use OIDC workload identity (GitHub Actions → AWS IRSA, GCP Workload Identity) rather than long-lived access keys.

### Secrets injection

Never bake secrets into images or deployment manifests. Inject them at runtime from a trusted source:

- **Vault agent sidecar** — a secrets management sidecar injects secrets into the pod filesystem or environment at startup and rotates them without restart.
- **Kubernetes External Secrets Operator** — syncs secrets from AWS Secrets Manager, HashiCorp Vault, or GCP Secret Manager into Kubernetes Secrets automatically.
- **Cloud-native workload identity** — services authenticate to cloud APIs using instance identity (IRSA, Workload Identity Federation) with no stored credential at all.

See [Secrets Management](../2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md).

## Environment parity and configuration security

- Use the same base image and the same configuration parameters across environments — the only differences should be externally injected (vault paths, endpoint URLs, TLS certificates).
- Never disable security controls in lower environments to make testing easier. A control disabled in staging often gets forgotten and reaches production.
- Configuration drift between environments is a leading cause of "works in staging, fails in production" security incidents. IaC and GitOps eliminate drift by making configuration declarative.

## Common pitfalls and anti-patterns

- **Manual deployments with shared credentials** — no audit trail, broad permissions, and credentials that are never rotated. Replace with automated pipelines and workload identity.
- **`latest` tags in production** — a mutable tag means any registry push can change what runs in production. Use digest-pinned references.
- **Admission control in audit-only mode forever** — many teams set admission controllers to warn but never enforce, defeating the purpose. Set a deadline to switch to enforcement.
- **Secrets in environment variables at build time** — environment variables leak into logs, crash dumps, and `/proc` on Linux. Use mounted secret files or vault agent injection instead.
- **No rollback plan** — deployment without a tested rollback plan is high-risk. Verify rollback in staging before every major production deploy.

## Maturity progression

**Starter** — Deploy via reviewed PRs to a private registry. Use a scoped deploy identity. Inject secrets from a vault rather than baking them in. Document a manual rollback procedure.

**Intermediate** — GitOps with Argo CD or Flux. Admission control enforcing signed images (Kyverno/policy-controller). Canary or blue-green delivery for tier-1 services. Automated rollback on health signals. Image digest pinning in all manifests.

**Advanced** — Full SLSA provenance verification at admission. Zero standing credentials — all deploy identities are short-lived OIDC tokens. Progressive delivery with automated promotion gates (error rate, latency, security signals). Configuration drift detection and auto-remediation. Deployment decisions logged to an immutable audit store.

## Metrics and KPIs

- **Deployment frequency** — higher frequency with stable failure rates indicates a healthy deployment process.
- **Change failure rate** — percentage of deployments causing incidents or rollbacks; security-related failures tracked separately.
- **Mean time to restore (MTTR)** — time from a bad deployment detection to rollback completion.
- **Policy violation blocks at admission** — number of deployments rejected by admission control; should reach zero as teams fix upstream processes.
- **Percentage of workloads with digest-pinned images** — target 100% for production.

---

## Tools[^1]

### Open-source

- [Argo CD](https://argo-cd.readthedocs.io/) — Declarative GitOps continuous delivery for Kubernetes; provides a UI dashboard for deployment status, drift detection, and rollback.
- [Argo Rollouts](https://argoproj.github.io/rollouts/) — Progressive delivery controller for Kubernetes: canary, blue-green, and automated analysis-based promotion.
- [Flux](https://fluxcd.io/) — GitOps toolkit for keeping clusters in sync; lightweight and composable; strong multi-tenancy and multi-cluster support.
- [Kyverno](https://kyverno.io/) — Kubernetes admission policy engine including image signature verification, resource validation, and mutation; no Rego required.
- [Sigstore policy-controller](https://github.com/sigstore/policy-controller) — Enforces cosign image signature and attestation policies at Kubernetes admission; integrates with Fulcio and Rekor.
- [External Secrets Operator](https://external-secrets.io/) — Syncs secrets from external vaults (AWS, GCP, Azure, Vault) into Kubernetes Secrets; avoids storing secrets in git.

### Commercial

- [Harness](https://www.harness.io/) — CI/CD and progressive delivery with built-in governance policies, approval workflows, and audit trails.
- [Octopus Deploy](https://octopus.com/) — Release management and deployment automation with environment promotion gates and change management integration; strong for non-Kubernetes workloads.

---

### Links

[^1]: Listed in alphabetical order.
