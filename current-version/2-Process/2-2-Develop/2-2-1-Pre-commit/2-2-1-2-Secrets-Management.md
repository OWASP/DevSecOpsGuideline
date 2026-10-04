# Secrets Management

Hardcoded secrets — API keys, passwords, tokens, private keys — are one of the most common and most damaging mistakes in software delivery. Once a secret reaches a git repository it must be considered compromised: history is hard to scrub, repos get cloned and forked, and automated bots scan public commits within seconds of a push. Secrets management spans **preventing** secrets from being committed and **handling** the secrets applications legitimately need at runtime.

## Why this matters

A single leaked AWS access key can result in complete account takeover, data exfiltration, and cloud bill fraud within minutes. The 2022 Toyota source code exposure and numerous cloud breaches trace back to credentials committed to source control. Preventing secrets from entering repositories is one of the highest-impact, lowest-effort security investments a team can make.

## Detecting and preventing leaked secrets

Apply detection at every layer — defense in depth works here too:

### Layer 1: Pre-commit (local)

Block secrets before they enter history. This is the cheapest catch because no pipeline time is consumed and no rotation is required.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1
    hooks:
      - id: gitleaks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: detect-private-key
```

See [Pre-commit](2-2-1-1-Pre-commit.md) for full framework setup.

### Layer 2: CI pipeline scanning

Mirror the same detection server-side so it cannot be bypassed with `--no-verify`. Run on every pull request and on full git history at least weekly.

```yaml
# GitHub Actions example
- name: Secret scan (TruffleHog)
  uses: trufflesecurity/trufflehog@v3.97.9   # pin to a release tag or full commit SHA, not @main
  with:
    path: ./
    base: ${{ github.event.repository.default_branch }}
    head: HEAD
    extra_args: --only-verified
```

### Layer 3: Push protection

Platform-level push protection (GitHub Secret Scanning push protection, GitLab secret detection) rejects pushes that contain recognized secret patterns server-side, before the commit is accepted. Enable it for all repositories — it is free on public repositories and, for private ones, available through GitHub Secret Protection (formerly part of GitHub Advanced Security); GitLab offers secret push protection on its paid tiers. It is a high-signal defense that catches secrets before they ever land in history.

### Layer 4: Historical scanning

New commits are not the only risk. Periodically scan full git history to catch secrets committed before scanning was in place.

```bash
# Full-history scan with TruffleHog
trufflehog git file://. --only-verified --fail
```

### Layer 5: Public exposure monitoring

Subscribe to GitHub secret scanning alerts (for public repos) and consider services that monitor paste sites and code-hosting platforms for your organization's credential patterns.

## Incident response for a leaked secret

If a secret is discovered in history:

1. **Rotate it immediately** — revoke the exposed credential in the issuing system first, before anything else. Removing it from history does not protect you; bots may have already scraped it.
2. **Audit usage logs** — check the credential's access logs for unauthorized use.
3. **Clean history (optional)** — use `git filter-repo` or BFG Repo Cleaner to remove the secret, then force-push and notify all cloners. This is secondary to rotation.
4. **Document and notify** — follow your incident response process; if personal data was accessible via the credential, privacy breach obligations may apply.

## Managing the secrets applications need at runtime

Applications and pipelines legitimately need credentials. The question is how to provide them safely.

### Never do this

- Hardcode secrets in source code.
- Store secrets in `.env` files committed to the repo.
- Bake secrets into container images at build time.
- Pass secrets as plain-text environment variables in CI job definitions.
- Share secrets in Slack, email, or Confluence pages.
- Hand long-lived credentials to AI coding agents or paste them into prompts; give agents scoped, short-lived credentials instead.

### Use centralized secret vaults

A dedicated secrets manager is the foundation:

- Secrets are stored encrypted with access controls and audit logs.
- Applications retrieve secrets at runtime via API, not at build time.
- Access is controlled by identity (IAM role, service account, workload identity) rather than by shared passwords.

```bash
# HashiCorp Vault: read a secret at runtime
vault kv get -field=api_key secret/myapp/prod
```

### Use dynamic / short-lived secrets

Static, long-lived credentials are a liability — if leaked, they remain valid until someone notices and rotates them. Dynamic secrets expire automatically:

```hcl
# Vault database secrets engine — generates a PostgreSQL credential valid for 1 hour
path "database/creds/my-role" {
  capabilities = ["read"]
}
```

HashiCorp Vault (or its open-source fork OpenBao), AWS Secrets Manager, and similar platforms can generate database credentials, cloud IAM credentials, and TLS certificates on demand with a short TTL.

### Use workload identity / OIDC for CI/CD

The strongest pattern for CI/CD pipelines: no long-lived cloud credentials stored anywhere. Instead, the CI platform issues a short-lived OIDC token that the cloud provider's IAM validates, granting a scoped role.

```yaml
# GitHub Actions — OIDC-based AWS access (no stored AWS keys)
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@v6   # pin to a commit SHA in production
    with:
      role-to-assume: arn:aws:iam::123456789012:role/my-github-actions-role
      aws-region: us-east-1
```

This eliminates AWS access keys from GitHub secrets entirely. Apply the same pattern for GCP (Workload Identity Federation) and Azure (federated credentials).

### Rotation

Automate rotation so credentials change on a schedule and after any potential exposure:

- Cloud secret managers (AWS Secrets Manager, Azure Key Vault, GCP Secret Manager) support automatic rotation, often through Lambda or Function hooks.
- Vault and OpenBao support lease renewal and automatic rotation for supported secret engines.
- Track rotation cadence per secret type; critical credentials (production database passwords) should rotate more frequently than low-risk ones.

### Least privilege and scoping

Every secret should grant the minimum access needed, for the minimum time:

- A CI job that only reads from S3 should not have a credential that can also delete objects or access other buckets.
- Scope API keys to specific endpoints or operations where the platform supports it.
- Use separate credentials per environment — never share a production credential with staging or development.

## Metrics

- Number of secrets detected at pre-commit vs CI vs in production (pre-commit share should be highest and rising).
- Number of active long-lived credentials vs short-lived / dynamic credentials (drive toward dynamic).
- Mean time to rotate a credential after discovery.
- Percentage of CI pipelines using OIDC / workload identity vs stored static keys.
- Age distribution of static credentials in use — aged credentials are a risk indicator.

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Gitleaks as a pre-commit hook, or TruffleHog in CI; `.env` files in `.gitignore`; basic secret rotation on request |
| Developing | CI pipeline scanning on all PRs; push protection enabled; secrets stored in a vault; no static cloud keys in CI |
| Defined | Dynamic secrets for databases and cloud; OIDC for all CI/CD cloud access; automated rotation with audit logging |
| Advanced | Zero static credentials in production; secrets access tied to workload identity and attested pipeline provenance; anomaly detection on secret access patterns |

---

## Tools[^1]

### Open-source

- [detect-secrets](https://github.com/Yelp/detect-secrets) — Yelp's enterprise-grade secret detector. Maintains a baseline file of accepted findings so teams can manage existing issues without noisy blocking.
- [External Secrets Operator](https://external-secrets.io/) — Kubernetes operator that syncs secrets from external managers (AWS, Azure, GCP, Vault, and others) into native Kubernetes Secrets so manifests never contain secret values.
- [Gitleaks](https://github.com/gitleaks/gitleaks) — Fast, widely adopted secret scanner for git repos, history, and CI pipelines. Configurable rule sets and pre-commit hook support.
- [Infisical](https://github.com/Infisical/infisical) — Open-source (MIT core) secrets management platform with a developer-friendly UI, CLI, and Kubernetes operator. Some advanced features such as dynamic secrets and rotation are in paid tiers.
- [OpenBao](https://openbao.org/) — Community-driven, MPL-2.0 fork of Vault maintained under the Linux Foundation (OpenSSF). API-compatible with Vault for dynamic secrets, PKI, and multiple auth methods; self-hosted only.
- [SOPS](https://github.com/getsops/sops) — Encrypts values inside YAML, JSON, and ENV files using KMS, age, or PGP keys, so encrypted secrets can live in git (commonly used with GitOps). Keys must still be managed and rotated.
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) — Finds and actively *verifies* leaked credentials (confirms the credential is still valid) across git history, S3, Jira, Slack, and more.

### Commercial / managed

- [1Password Secrets Automation](https://developer.1password.com/) — Syncs secrets from 1Password vaults to apps and infrastructure via CLI, SDKs, and Kubernetes operator.
- [Akeyless](https://www.akeyless.io/) — SaaS zero-knowledge platform for secrets, certificates, and key management with a free tier.
- [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/) — Managed secret storage with native rotation for RDS, Redshift, and custom Lambda rotators.
- [Azure Key Vault](https://azure.microsoft.com/en-us/products/key-vault/) — Managed key and secret storage for Azure workloads.
- [CyberArk Secrets Manager](https://www.cyberark.com/) — Enterprise secrets management for applications, containers, and CI/CD pipelines.
- [Doppler](https://www.doppler.com/) — SecretOps platform that syncs secrets across environments and injects them at runtime. Good developer UX for teams without a dedicated Vault deployment.
- [GCP Secret Manager](https://cloud.google.com/secret-manager) — Google Cloud's managed secret storage with IAM-based access control and audit logging.
- [GitGuardian](https://www.gitguardian.com/) — Secrets detection across repos, CI, and developer machines (including the `ggshield` CLI), with incident workflow and remediation tracking. Free for individual developers and small teams.
- [HashiCorp Vault](https://developer.hashicorp.com/vault) — Full-featured secrets management platform. Supports dynamic secrets, leasing, rotation, PKI, and multiple auth methods. Source-available under the Business Source License since August 2023 (previously open source); enterprise and managed (HCP) editions are available.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub — About secret scanning](https://docs.github.com/en/code-security/secret-scanning/about-secret-scanning)
- [HashiCorp Vault tutorials](https://developer.hashicorp.com/vault/tutorials)
- [GitHub OIDC — Configuring OpenID Connect in AWS](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
