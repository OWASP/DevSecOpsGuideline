# Dependency Management and Cooldown Policies

[SCA](2-3-2-1-Software-Composition-Analysis.md) tells you which dependencies are known to be vulnerable. Dependency management decides **which versions you accept in the first place, and when**. Most recent registry compromises (hijacked maintainer accounts, poisoned releases, self-propagating worms) were detected and pulled within hours or days, but not before automated updates installed them. Deterministic builds, a deliberate delay before adopting new releases, and controlled package sources close much of that window.

## Lockfiles and pinning

A lockfile records the exact resolved version (and, in most ecosystems, the integrity hash) of every direct and transitive dependency. Commit it, review changes to it, and make CI fail if it is out of date.

| Ecosystem | Lockfile | Reproducible install command |
|---|---|---|
| npm | `package-lock.json` | `npm ci` |
| pnpm | `pnpm-lock.yaml` | `pnpm install --frozen-lockfile` |
| Yarn | `yarn.lock` | `yarn install --immutable` |
| Python (uv) | `uv.lock` | `uv sync --locked` |
| Python (pip) | `requirements.txt` with hashes | `pip install --require-hashes -r requirements.txt` |
| Go | `go.sum` | `go mod verify` |
| Rust | `Cargo.lock` | `cargo build --locked` |

- Treat lockfile diffs in pull requests as code: unexpected new packages, changed registry URLs, or removed integrity hashes are red flags.
- Pin base images and CI actions the same way (digests and commit SHAs); see [CI/CD Pipeline Security](../2-3-6-Supply-Chain-Security/2-3-6-3-CICD-Pipeline-Security.md).
- Avoid floating ranges (`latest`, `*`) in application manifests. Libraries may use ranges; applications should resolve them through the lockfile.

## Cooldown (minimum release age) policies

A **cooldown** delays adoption of a newly published version for a fixed period (commonly 3-7 days, longer for major bumps) so that malware scanners, registry staff, and the community can catch bad releases first. It trades a short delay on features and non-urgent fixes for protection against the most common attack pattern: a malicious version that is live for hours.

Update bots:

```json
// renovate.json
{
  "extends": ["config:recommended"],
  "minimumReleaseAge": "7 days",
  "internalChecksFilter": "strict"
}
```

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "daily"
    cooldown:
      default-days: 7
      semver-major-days: 30
      semver-minor-days: 7
      semver-patch-days: 3
```

Package managers (units differ between tools, so do not copy numbers blindly):

```ini
# .npmrc (npm >= 11.10) - value in days
min-release-age=7
```

```yaml
# pnpm-workspace.yaml (pnpm >= 10.16) - value in minutes
minimumReleaseAge: 10080
minimumReleaseAgeStrict: true   # fail instead of falling back to an older-than-allowed rule
```

```toml
# pyproject.toml (uv >= 0.9.17 for relative durations)
[tool.uv]
exclude-newer = "7 days"
```

```bash
# pip >= 26.1: relative duration; pip 26.0 accepts absolute timestamps only
pip install --uploaded-prior-to=P7D -r requirements.txt
```

Yarn (`npmMinimalAgeGate`) and Bun (`minimumReleaseAge` in `bunfig.toml`) offer equivalents; check the current documentation for units and minimum versions.

Operational notes:

- Renovate's `internalChecksFilter: "strict"` (the default) prevents branches and PRs from being created until the age check passes. Renovate documents that `minimumReleaseAge` is not applied to every update type (for example lockfile-only maintenance), so review its security presets (`security:minimumReleaseAge*`).
- Dependabot's `cooldown` applies to version updates only; security updates are not delayed.
- Enforce the policy in the package manager as well as in the bot, so manual `npm install` or `pip install` by developers and CI is covered too.

### Emergency-patch exceptions

A cooldown must never delay a fix for an actively exploited vulnerability. Define the exception up front:

- Security updates raised from advisories (Dependabot security updates, Renovate `vulnerabilityAlerts`) bypass the delay by design; verify this behavior in your own configuration, because a later `packageRules` entry can re-apply an age to matching packages.
- Allow a documented override for named packages (`minimumReleaseAgeExclude` in pnpm, `exclude` in Dependabot cooldown, `min-release-age-exclude` in recent npm) rather than disabling the policy globally.
- Require a human review of the release (changelog, publisher, provenance) before overriding, and record who approved it and why.

## Private registries and proxies

Route all installs through an internal registry or proxy (Artifactory, Nexus, Verdaccio, cloud-provider artifact registries) instead of public registries directly:

- Cache approved versions so builds survive upstream outages and yanked or deleted packages.
- Enforce policy centrally: block known-malicious packages, license violations, and versions younger than the cooldown.
- Give CI read-only, short-lived credentials; publish credentials belong only to release pipelines.

## Dependency confusion, typosquatting and slopsquatting

- **Dependency confusion** — an attacker publishes a public package with the same name as your internal one, often with a higher version. Reserve your namespace or scope on public registries, map internal scopes to the private registry explicitly, and prefer a single virtual repository that decides precedence. In Python, `--extra-index-url` merges indexes and is a classic cause; with uv, review `index-strategy` and use pinned indexes per package.
- **Typosquatting** — near-identical names (`reqeusts`). Review new dependencies before adding them; check publisher, age, download history, and repository link.
- **Slopsquatting** — attackers register package names that AI coding assistants commonly hallucinate. Verify that any AI-suggested dependency exists, is the intended project, and is not brand new; see [IDE and AI-assisted development](../../2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md).

## Install-script risk

Install-time lifecycle hooks (`preinstall`, `postinstall`, `setup.py`, build scripts) run arbitrary code on developer machines and CI runners before any scanner sees the code.

- npm: `npm ci --ignore-scripts` (or `ignore-scripts=true` in `.npmrc`), then explicitly rebuild the few packages that need native builds.
- pnpm (v10+) does not run dependency lifecycle scripts by default; approve exceptions with `onlyBuiltDependencies`.
- Python: prefer wheels (`--only-binary :all:`) over source distributions, which execute build code.
- Run installs in CI without secrets in the environment and with restricted egress.

## Malicious package detection and provenance

- Check new and updated dependencies against malicious-package data (OSV, which includes the OpenSSF malicious-packages feed) and behavioral analysis tools (GuardDog, Socket).
- Verify provenance where available: `npm audit signatures` checks registry signatures and provenance attestations; PyPI supports attestations for packages published through Trusted Publishing. Provenance proves where a package was built, not that the code is benign; treat a missing or changed publisher or provenance as a review trigger.
- Prefer dependencies whose maintainers publish via **trusted publishing** (OIDC from CI to the registry) instead of long-lived tokens.
- Record the result in your [SBOM](../2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) pipeline so a later malware disclosure can be mapped to every affected build.

## Common pitfalls and anti-patterns

- **Not committing lockfiles** or running `npm install` / `pip install` in CI, which re-resolves versions on every build.
- **Cooldown configured only in the bot** — developers and CI still install the newest versions manually.
- **No emergency path** — teams that cannot fast-track a KEV-listed fix disable the cooldown entirely.
- **Mixing units** when copying settings between npm (days), pnpm (minutes), and others.
- **Mixed public and private indexes** without explicit precedence, enabling dependency confusion.
- **Auto-merging updates without a cooldown or CI gate** — a poisoned release goes straight to production.
- **Running install scripts with production secrets** available in the build environment.

## Maturity progression

**Starter** — Commit lockfiles and use frozen-install commands in CI. Enable Dependabot or Renovate with a short cooldown (3-7 days). Review new direct dependencies manually.

**Intermediate** — Enforce release age in the package managers too. Route installs through an internal proxy with malicious-package blocking. Disable install scripts by default with an allowlist. Verify signatures and provenance in CI.

**Advanced** — Tiered cooldowns by update type and package criticality with an audited emergency-override process. Continuous malicious-package monitoring tied to SBOM inventory. Namespace reservation on public registries. Isolated, egress-restricted dependency installation.

## Metrics and KPIs

| Metric | Target |
|---|---|
| Repositories with committed lockfile and frozen installs in CI | 100% |
| Repositories with a cooldown enforced (bot and package manager) | > 90% |
| Emergency overrides with recorded approval | 100% |
| Installs going through the internal proxy | 100% of CI |
| Time to fix KEV-listed dependency vulnerabilities | < 24 hours |

---

## Tools[^1]

### Open-source

- [Dependabot](https://docs.github.com/en/code-security/dependabot) — GitHub-native version and security update PRs; supports `cooldown` for version updates.
- [GuardDog](https://github.com/DataDog/guarddog) — Scans PyPI, npm, Go, and other packages for malicious behavior using heuristics and Semgrep rules.
- [OSV-Scanner](https://github.com/google/osv-scanner) — Scans lockfiles against OSV, including malicious-package advisories.
- [pnpm](https://pnpm.io/) — Package manager with `minimumReleaseAge` and default blocking of dependency install scripts.
- [Renovate](https://github.com/renovatebot/renovate) — Update automation with `minimumReleaseAge`, security presets, and broad ecosystem coverage.
- [uv](https://github.com/astral-sh/uv) — Python package manager with a lockfile and `exclude-newer` release-date filtering.
- [Verdaccio](https://verdaccio.org/) — Lightweight private npm registry and caching proxy.

### Commercial

- [JFrog Artifactory](https://jfrog.com/artifactory/) — Universal repository manager with remote-repository proxying and curation policies.
- [Socket](https://socket.dev/) — Detects malicious and risky package behavior, including install scripts and obfuscation.
- [Sonatype Nexus Repository](https://www.sonatype.com/products/sonatype-nexus-repository) — Repository manager and proxy; pairs with Nexus Firewall to block malicious components.

---

### Links

[^1]: Listed in alphabetical order.
