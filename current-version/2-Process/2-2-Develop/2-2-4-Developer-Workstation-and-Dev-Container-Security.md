# Developer Workstation and Dev Container Security

The developer's machine is where source code, signing keys, cloud credentials, and package-manager tokens all meet — and it routinely executes third-party code (dependencies, extensions, build scripts, AI agents). A compromised workstation bypasses nearly every downstream control, because the attacker inherits the developer's identity and trust. Securing the development environment means hardening the endpoint, limiting what lives on it, and, where possible, moving work into isolated, disposable environments.

## Why this matters

Attackers target developers because their access is broad and their tooling runs untrusted code by design. Malicious packages with install scripts, trojanized IDE extensions, and stolen browser sessions or tokens are all documented routes from a developer laptop to source repositories, CI secrets, and production. Treat the workstation as part of the software supply chain.

## Endpoint baseline

Apply a consistent baseline to every device that can reach source code or internal systems, managed through MDM or endpoint management:

- **Full-disk encryption** — FileVault (macOS), BitLocker (Windows), or LUKS (Linux), with recovery keys escrowed centrally.
- **Patching** — automatic OS, browser, and toolchain updates with a defined maximum age.
- **Screen lock, standard (non-admin) accounts, and a host firewall** enabled by default.
- **Endpoint detection and response (EDR)** and device-compliance checks, with access to repositories and cloud consoles conditional on device posture.
- **Application control** where practical, so unknown binaries cannot run unreviewed.
- **Separation of duties** — avoid mixing personal browsing profiles, personal accounts, and production access on one profile.

## Secrets on the laptop

Assume anything on disk can be read by malware running as the developer. Reduce what is there:

- Do not keep long-lived cloud keys, tokens, or `.env` files with production values on laptops; see [Secrets Management](2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md).
- Prefer short-lived credentials from SSO (for example, cloud CLI SSO login) over static access keys in `~/.aws/credentials` or similar files.
- Store tokens in the OS keychain or a credential helper rather than plain-text config files.
- Run a secret scanner against the local filesystem and shell history periodically, and keep scanning pre-commit hooks enabled.
- Scope personal access tokens narrowly, give them an expiry, and prefer fine-grained tokens over classic all-access ones.

## SSH, signing keys, and hardware keys

Keys that can push code or sign commits and releases deserve the strongest protection:

- Use **hardware-backed keys** (FIDO2 security keys) for SSH and for account MFA. OpenSSH supports FIDO2-backed `ed25519-sk` keys, so the private key cannot be copied off the device.
- Use phishing-resistant MFA (passkeys or security keys) on the source host, identity provider, and cloud accounts.
- **Sign commits and tags** so provenance can be verified. SSH signing works with the same key you already use:

```bash
# Generate a hardware-backed SSH key (requires a FIDO2 security key)
ssh-keygen -t ed25519-sk -C "dev@example.com"

# Sign commits with an SSH key
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519_sk.pub
git config --global commit.gpgsign true
```

- Alternatively, use keyless signing with Sigstore `gitsign`, which ties signatures to an identity-provider login instead of a long-lived key.
- Use an SSH agent that requires confirmation or touch per use, and avoid forwarding the agent to untrusted hosts.

## Browser and IDE extension risk

Extensions run with the developer's privileges and update silently, which makes them an attractive supply-chain target:

- Maintain an **allowlist** of approved IDE and browser extensions; block installation of others through managed policy.
- Review publisher, permissions, and update history before approving; remove unused extensions.
- Disable automatic updates for high-privilege extensions or pin versions where the marketplace supports it, and review changes on update.
- Be wary of workspace trust prompts: opening an untrusted repository can run tasks, debuggers, or extension code. Keep the IDE's restricted/untrusted mode enabled by default and only trust repositories you have reviewed.

## Package-manager install-script risk

Installing a dependency can execute arbitrary code on the developer machine through lifecycle scripts. Reduce exposure:

```ini
# .npmrc (npm)
ignore-scripts=true
```

- Disable or allowlist install scripts and enable only for the few packages that need them (for example, native-module builds); recent versions of pnpm restrict dependency build scripts by default, and npm supports `ignore-scripts`. Check your package manager's current documentation for the supported allowlist setting.
- Enforce a minimum release age ("cooldown") before adopting new versions, where supported (npm `min-release-age`, available from npm 11.10; pnpm `minimumReleaseAge`). Note that the two use different units, and that age gates only help against compromises that are detected quickly.
- Commit lockfiles, install with `npm ci` or the equivalent frozen-lockfile mode, and route installs through an internal registry proxy.
- Verify new dependencies exist and are the intended package, especially when copied from AI-generated snippets.

## Ephemeral and containerized environments

The strongest control is to avoid long-lived, hand-configured machines for risky work:

- **Dev containers** define the toolchain in version-controlled configuration (`devcontainer.json`) so every developer gets the same, reviewable environment, and the container boundary limits what untrusted code can touch.
- **Cloud development environments** (for example, GitHub Codespaces or Coder) keep source code and credentials off the laptop and are destroyed after use. Apply organization policies for allowed images, secrets, and idle timeouts.
- **Disposable VMs or containers** are a good fit for reviewing unknown repositories, running untrusted dependencies, and running AI agents (see [AI Agent and MCP Security](2-2-5-AI-Agent-and-MCP-Security.md)).

Dev container configuration is code and should be reviewed as such:

```json
// .devcontainer/devcontainer.json
{
  "name": "app-dev",
  "image": "mcr.microsoft.com/devcontainers/base:ubuntu",
  "remoteUser": "vscode",
  "containerEnv": { "NODE_ENV": "development" },
  "runArgs": ["--cap-drop=ALL", "--security-opt=no-new-privileges"],
  "postCreateCommand": "npm ci --ignore-scripts"
}
```

Avoid `--privileged`, mounting the Docker socket, mounting the host home directory, and forwarding broad credentials into the container. Pin base images by digest where practical, and treat `postCreateCommand`, features, and lifecycle hooks as code that executes automatically when the environment opens.

## Least-privilege cloud credentials for development

- Give developers access to **development accounts or sandboxes**, not production, and use time-limited elevation (just-in-time access) for production troubleshooting.
- Authenticate through SSO with short session durations; avoid static IAM user keys.
- Use separate roles for read-only exploration and for deployment; deployments should run from CI using OIDC, not from laptops.
- Alert on and log console and API use outside expected patterns.

## Remote development

Remote SSH, tunnels, and port forwarding extend the attack surface. Require authenticated, encrypted channels; do not expose development servers or debug ports publicly; restrict forwarded ports to private visibility; and keep the remote host patched and access-logged. Prefer identity-aware access over open inbound ports.

## Common pitfalls and anti-patterns

- **Long-lived production keys in `~/.aws` or `.env`** — one infostealer away from a breach.
- **"Works on my machine" snowflake setups** — unreviewed, unreproducible environments that cannot be audited or rebuilt after compromise.
- **Unrestricted extension installs** — extensions treated as harmless productivity tools.
- **Dev containers run as `--privileged` or with the Docker socket mounted** — this removes the isolation the container was meant to provide.
- **Trusting every repository on open** — workspace trust prompts dismissed by reflex.
- **Software keys with no passphrase and no expiry** — SSH keys copied between machines indefinitely.

## Maturity progression

| Level | Practice |
|---|---|
| Starter | Disk encryption and auto-updates enforced; MFA on source host; pre-commit secret scanning; no secrets committed to repos |
| Intermediate | MDM with posture checks; extension allowlist; signed commits; SSO-based short-lived cloud credentials; install scripts restricted; dev containers for common projects |
| Advanced | Hardware-backed keys and phishing-resistant MFA everywhere; cloud or disposable environments for untrusted work and AI agents; device posture gates repository access; just-in-time production access; workstation telemetry feeds detection |

## Metrics and KPIs

- Percentage of developer devices compliant with the endpoint baseline.
- Percentage of developers using hardware-backed or phishing-resistant MFA.
- Percentage of commits signed on protected branches.
- Count of long-lived static credentials found on developer endpoints (drive toward zero).
- Percentage of repositories with a reviewed dev container or equivalent standard environment.
- Mean time to rebuild a developer environment after suspected compromise.

---

## Tools[^1]

### Open-source

- [Coder](https://github.com/coder/coder) — Self-hosted platform for provisioning cloud development environments from Terraform templates.
- [Dev Containers specification](https://containers.dev/) — Open specification and tooling for defining reproducible containerized development environments.
- [DevPod](https://github.com/loft-sh/devpod) — Client-only tool that creates dev container-based environments on any backend (local Docker, cloud, Kubernetes).
- [Gitleaks](https://github.com/gitleaks/gitleaks) — Secret scanner usable in pre-commit hooks and against local directories.
- [Sigstore gitsign](https://github.com/sigstore/gitsign) — Keyless Git commit signing using short-lived certificates tied to an identity-provider login.
- [osquery](https://osquery.io/) — Exposes endpoint state as SQL tables for compliance and inventory checks.

### Commercial

- [1Password](https://developer.1password.com/docs/ssh/) — Password manager with an SSH agent and commit-signing support, keeping keys out of plain files.
- [GitHub Codespaces](https://github.com/features/codespaces) — Managed cloud development environments based on dev containers, with organization policy controls.
- [GitGuardian ggshield](https://github.com/GitGuardian/ggshield) — CLI that scans for secrets on developer machines and in pre-commit hooks (free tier available).
- [YubiKey](https://www.yubico.com/) — FIDO2 hardware security keys for MFA and hardware-backed SSH keys.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [GitHub — Managing Codespaces security](https://docs.github.com/en/codespaces/managing-codespaces-for-your-organization/managing-secrets-and-security-for-codespaces)
- [GitHub — About commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification)
- [OpenSSH — FIDO/U2F security keys](https://www.openssh.com/txt/release-8.2)
- [Secrets Management](2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md)
- [AI Agent and MCP Security](2-2-5-AI-Agent-and-MCP-Security.md)
