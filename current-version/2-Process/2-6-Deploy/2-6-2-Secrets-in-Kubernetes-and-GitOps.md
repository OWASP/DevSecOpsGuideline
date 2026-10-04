# Secrets in Kubernetes and GitOps

[Deployment](2-6-1-Deploy.md) pipelines need to hand credentials to workloads without putting them in images, manifests, or git history. Kubernetes and GitOps make this harder: GitOps wants *everything* in git, while secrets must never be there in plaintext. This page covers the patterns that resolve the conflict. For secret hygiene before code reaches the cluster, see [Secrets Management](../2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md).

## Why Kubernetes Secrets are not enough on their own

- A `Secret` value is only **base64-encoded**, not encrypted. Anyone who can read the object (or a manifest in git) can decode it: `kubectl get secret db -o jsonpath='{.data.password}' | base64 -d`.
- By default, Secrets are stored **unencrypted in etcd**; etcd backups and snapshots expose them too.
- Anyone who can create a Pod in a namespace can mount any Secret in that namespace, so `get`/`list`/`watch` on Secrets and Pod creation are effectively equivalent to reading them.
- Secrets exposed as environment variables leak into logs and crash dumps; mounted files are safer.

## Harden the built-in mechanism

**Encrypt etcd at rest** with an `EncryptionConfiguration` passed to the API server (`--encryption-provider-config`). Prefer a KMS provider (KMS v2) so the key encryption key lives outside the cluster; managed Kubernetes services usually offer this as an option.

```yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources: ["secrets"]
    providers:
      - kms:
          apiVersion: v2
          name: my-kms
          endpoint: unix:///var/run/kms/socket.sock
      - identity: {}   # last: allows reading data written before encryption was enabled
```

After enabling, rewrite existing Secrets (`kubectl get secrets -A -o json | kubectl replace -f -`) so stored data is re-encrypted.

**Restrict access with RBAC:**

- Never grant `get`, `list`, or `watch` on `secrets` cluster-wide; `list` returns values. Scope to named Secrets with `resourceNames` where possible.
- Limit who can `exec` into Pods or create Pods in sensitive namespaces.
- Audit Secret access via API server audit logs and alert on unusual reads.

## Keep secrets out of git: choosing a pattern

| Pattern | Secret value lives in | Git contains | Typical fit |
|---|---|---|---|
| External Secrets Operator | External store (cloud secret manager, Vault/OpenBao) | A reference (`ExternalSecret`) | Central store, rotation, multiple clusters |
| Secrets Store CSI Driver | External store | A `SecretProviderClass` reference | Mount directly as files, optionally without a Secret object |
| SOPS | Git, encrypted with age or KMS | Encrypted file | Small teams, no external store dependency |
| Sealed Secrets | Git, encrypted to the cluster's controller key | `SealedSecret` ciphertext | Simple, cluster-scoped, no external store |

Prefer **referencing** patterns (ESO, CSI) when an external secret manager already exists: git never holds ciphertext, rotation is centralised, and revoking access does not require rewriting history.

```yaml
# External Secrets Operator: git holds only this reference
apiVersion: external-secrets.io/v1
kind: ExternalSecret
metadata:
  name: myapp-db
spec:
  refreshInterval: 1h
  secretStoreRef:
    kind: ClusterSecretStore
    name: aws-secrets-manager
  target:
    name: myapp-db
  data:
    - secretKey: password
      remoteRef:
        key: myapp/production/database
        property: password
```

```bash
# SOPS with age: encrypt only the values under data/stringData
sops --encrypt --age age1... \
  --encrypted-regex '^(data|stringData)$' secret.yaml > secret.enc.yaml
```

Encrypted-in-git patterns (SOPS, Sealed Secrets) put ciphertext in history permanently: if the private key ever leaks, every past version is exposed. Back up and rotate the decryption keys, and rotate the underlying secret values when keys change.

## GitOps flows with Argo CD and Flux

- **Flux** decrypts SOPS natively in the kustomize-controller:

```yaml
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: myapp
  namespace: flux-system
spec:
  interval: 10m
  path: ./apps/myapp
  prune: true
  sourceRef:
    kind: GitRepository
    name: fleet
  decryption:
    provider: sops
    secretRef:
      name: sops-age
```

- **Argo CD** has no built-in SOPS support; it relies on plugins (KSOPS, a config management plugin, or helm-secrets). Its documentation recommends populating secrets on the **destination cluster** (External Secrets Operator, Sealed Secrets) rather than injecting them during manifest generation, because generated manifests are cached in plaintext by the repo-server.
- Exclude the generated `Secret` from drift reconciliation if an operator owns its contents, and restrict who can view Secret resources in the GitOps UI.
- Keep the decryption key or cloud permissions scoped to the GitOps controller, one per environment.

## Workload identity instead of static credentials

The best secret is one that does not exist. Let pods authenticate to cloud APIs and secret stores with platform identity (EKS Pod Identity or IRSA, GKE Workload Identity Federation, Azure Workload Identity) or short-lived Kubernetes service-account tokens. Use the same approach for the External Secrets Operator and CSI provider themselves, so no bootstrap credential is stored in the cluster. Where a static credential is unavoidable, scope it to one workload and rotate it.

## Rotation

- Use a store that supports rotation or dynamic credentials (Vault and OpenBao database secrets engines, cloud secret manager rotation).
- ESO refreshes on `refreshInterval`; the Secrets Store CSI Driver can rotate mounted content when its rotation feature is enabled. Applications must **reload** values (file watch or rolling restart); a rotated Secret is not picked up by running processes that read it at startup.
- Rehearse emergency rotation: leaked secret, leaked SOPS/Sealed Secrets key, compromised store credential.

## Scanning repositories

Scan GitOps repositories like any other: pre-commit hooks and CI secret scanning (Gitleaks, TruffleHog, Trivy) catch base64-encoded `Secret` manifests committed by mistake. Add a policy (Kyverno, Gatekeeper, or a CI check) that rejects plaintext `kind: Secret` manifests with `data` or `stringData` in the GitOps repo, allowing only `ExternalSecret`, `SealedSecret`, or SOPS-encrypted files.

## Common pitfalls and anti-patterns

- **Committing base64 Secrets** and believing they are protected.
- **No etcd encryption**, or encryption enabled without rewriting existing Secrets.
- **Broad `list`/`get` on Secrets** for CI service accounts, operators, or developers.
- **Long-lived static cloud keys** stored as Kubernetes Secrets to reach a secret manager.
- **Never rotating SOPS or Sealed Secrets keys**, or losing the only copy of them.
- **Secrets as environment variables** and no application reload after rotation.
- **Injecting secrets during Argo CD manifest generation** without protecting the repo-server and its cache.

## Maturity progression

**Starter** — No plaintext secrets in git. Use SOPS or Sealed Secrets for encrypted-in-git delivery. Enable etcd encryption (or the managed-service equivalent) and restrict Secret RBAC.

**Intermediate** — Central secret manager with External Secrets Operator or the CSI driver. Workload identity for cloud access. CI secret scanning and a policy rejecting plaintext Secrets. Documented rotation runbook.

**Advanced** — KMS-backed encryption with key rotation, dynamic short-lived credentials, automatic reload on rotation, audit alerting on Secret reads, and regular rotation drills.

## Metrics and KPIs

- **Plaintext Secret manifests in GitOps repositories** — target 0.
- **Percentage of workloads using workload identity instead of static credentials** — track upward.
- **Secrets older than their rotation policy** — target 0.
- **Principals with `get`/`list` on Secrets cluster-wide** — minimised and reviewed.
- **Time to rotate a compromised secret** — measured in drills.

---

## Tools[^1]

### Open-source

- [Argo CD](https://argo-cd.readthedocs.io/) — GitOps controller; see its [secret management guidance](https://argo-cd.readthedocs.io/en/stable/operator-manual/secret-management/).
- [External Secrets Operator](https://external-secrets.io/) — Syncs secrets from external managers into Kubernetes Secrets.
- [Flux](https://fluxcd.io/) — GitOps toolkit with native SOPS decryption.
- [Gitleaks](https://github.com/gitleaks/gitleaks) — Detects secrets in repositories and git history.
- [OpenBao](https://openbao.org/) — Open-source secrets management fork of Vault, maintained under the Linux Foundation.
- [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) — Encrypts secrets so they are safe to store in git; decrypted by an in-cluster controller.
- [Secrets Store CSI Driver](https://secrets-store-csi-driver.sigs.k8s.io/) — Mounts secrets from external stores into pods as volumes.
- [SOPS](https://github.com/getsops/sops) — Encrypts values in YAML/JSON files using age, PGP, or cloud KMS.
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) — Finds and verifies leaked credentials.

### Commercial

- [HashiCorp Vault](https://www.vaultproject.io/) — Secrets management with dynamic credentials; Vault Enterprise and HCP Vault add support and governance features.
- Cloud secret managers — AWS Secrets Manager, Azure Key Vault, and Google Secret Manager, commonly used as ESO or CSI backends.

---

### Links

[^1]: Listed in alphabetical order.
