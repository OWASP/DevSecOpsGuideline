# Repository Hardening

The source repository is the single source of truth for what gets built and shipped. If an attacker can push malicious code, alter history, or weaken CI/CD protections, every downstream control inherits that compromise. A developer account takeover that reaches an unprotected repository is a supply-chain incident. **Repository hardening** locks down the repo itself so that what enters the pipeline is trustworthy.

## Branch and merge protection

Unprotected branches are the most common repository vulnerability. Every commit to a default or release branch without review is a potential injection point.

**GitHub branch protection settings to enable:**

```text
Branch protection rule for: main, master, release/*
  [x] Require a pull request before merging
       [x] Require approvals: 2
       [x] Dismiss stale pull request approvals when new commits are pushed
       [x] Require review from Code Owners
  [x] Require status checks to pass before merging
       [x] Require branches to be up to date before merging
       Status checks: ci/build, security/sast, security/secrets
  [x] Require conversation resolution before merging
  [x] Require signed commits
  [x] Do not allow bypassing the above settings
  [x] Restrict who can push to matching branches
  [x] Block force pushes
  [x] Allow deletions: NO
```

On GitHub, prefer **repository or organization rulesets** over classic branch protection rules where possible: rulesets can be layered, apply to many repositories at once, support an "evaluate" (dry-run) mode, and make bypass permissions explicit and auditable. GitLab offers equivalent protected branches, push rules, and merge request approval policies.

**CODEOWNERS** ensures that changes to high-risk paths require review from the team that owns them:

```text
# .github/CODEOWNERS
# Auth and crypto: require security team review
/src/auth/           @org/security-team
/src/crypto/         @org/security-team

# CI/CD configuration: require platform team + security review
/.github/workflows/  @org/platform-team @org/security-team
/Dockerfile          @org/platform-team
/terraform/          @org/platform-team @org/security-team
```

## Identity and access

### Human identities

- Grant the **minimum role** required. Most contributors need only Write access; Admin should be held by a small, named group.
- Enforce **MFA for all contributors** at the organization level. Do not allow HTTP basic auth or personal access tokens as the sole authentication method.
- Integrate with your **corporate identity provider** (SSO) so that offboarding automatically revokes repository access.
- Review access quarterly; remove dormant accounts — accounts that have not committed or reviewed in 90 days are an unnecessary attack surface.

### Machine identities

- **Deploy keys** — scope to a single repository, grant read-only unless write is strictly required, rotate on a schedule.
- **Bot accounts** — treat like service accounts: named, scoped, audited. Do not use a human's account as a bot.
- **Personal access tokens (PATs)** — enforce expiry, grant minimal scope, require documented justification for fine-grained PAT exceptions.
- **Prefer short-lived tokens** — use OIDC and workload identity wherever possible rather than long-lived PATs or service account keys. See [Secrets Management](2-2-1-2-Secrets-Management.md).

## Integrity of code and history

### Signed commits and tags

Commit signing lets consumers verify that a commit was made by the claimed author and has not been altered. Without signing, `git log --author` is trivially spoofable.

```bash
# Configure GPG signing globally
git config --global commit.gpgsign true
git config --global user.signingkey <your-gpg-key-id>

# Or use SSH signing (simpler key management)
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519.pub
git config --global commit.gpgsign true

# Or use Sigstore gitsign (keyless, ties signing to OIDC identity)
git config --global gpg.x509.program gitsign
git config --global gpg.format x509
git config --global commit.gpgsign true
```

Require signed commits in branch protection so unsigned commits are rejected server-side.

### Protect tags and releases

Tags feed the release pipeline. An attacker who can move or delete a tag can make a different commit ship as a release.

```bash
# GitHub: protect release tags with a tag ruleset (classic tag protection rules are deprecated)
# Settings > Rules > Rulesets > New tag ruleset: target v*, restrict updates and deletions
```

Where your platform supports it, also enable **immutable releases** so that published release assets and their tags cannot be modified or replaced after publication. Note that a tag alone is still mutable unless a ruleset blocks updates.
Sign release tags:

```bash
git tag -s v1.2.3 -m "Release v1.2.3"
git push origin v1.2.3
```

## Hardening the automation surface

CI/CD workflows have privileged access and are a high-value target. The repository itself is the attack surface for workflow injection.

### Restrict workflow permissions

Set least-privilege permissions at the workflow and job level:

```yaml
# Set read-only default permissions for the entire workflow
permissions:
  contents: read

jobs:
  build:
    permissions:
      contents: read
      packages: write   # only the jobs that need it get elevated scope
```

Never use `permissions: write-all` unless you have an explicit, documented reason.

### Pin third-party Actions to digest

Mutable tags (`@v3`, `@main`) can be silently updated to contain malicious code. Pin to immutable SHA digests:

```yaml
# Bad — mutable tag
- uses: actions/checkout@v4

# Good — pinned to immutable digest
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
```

GitHub can enforce this centrally: in the organization or repository **Actions > General** settings, enable *Require actions to be pinned to a full-length commit SHA* so unpinned workflows fail. Pinning protects against tag-hijacking incidents such as the 2025 `tj-actions/changed-files` compromise and the 2026 Trivy actions compromise.

Use [Dependabot for Actions](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/keeping-your-actions-up-to-date-with-dependabot) to keep digests current without manual tracking.

### Control fork pull request permissions

By default, workflows triggered by the `pull_request` event from forks run with a read-only token and no access to secrets, but they still execute code in your CI environment. Set explicit policies:

- In **Settings > Actions > General**, require approval before workflows run for all outside collaborators (or at least first-time contributors).
- Keep fork-triggered workflows on `pull_request`, and split any privileged follow-up (commenting, labeling, publishing) into a separate `workflow_run` workflow that never checks out or executes untrusted code.
- Disable sending write tokens and secrets to fork pull requests unless there is a documented need.

```yaml
# Dangerous: runs with secrets and a write token in the base repo context
on:
  pull_request_target:
    types: [opened, synchronize]
jobs:
  test:
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # checks out untrusted code - do not do this
```

Avoid `pull_request_target` combined with a checkout of untrusted PR code — it is a known attack vector for secret exfiltration and was the entry point of several real-world GitHub Actions compromises. Scan workflows with a tool such as [zizmor](https://github.com/zizmorcore/zizmor) to catch this pattern automatically.

## Platform security features

Enable the full suite of built-in platform protections:

| Feature | Platform | Purpose |
|---|---|---|
| Secret scanning + push protection | GitHub Secret Protection (free on public repos), GitLab | Block and alert on committed secrets |
| Dependabot / Dependency review | GitHub | Alert on and auto-PR vulnerable dependencies |
| Code scanning (CodeQL) | GitHub Code Security (free on public repos) | SAST integrated into PR workflow |
| Rulesets / protected branches | GitHub / GitLab | Central, auditable enforcement of branch, tag, and merge rules |
| Audit log | GitHub / GitLab | Track org-level events (member changes, settings changes) for incident investigation |
| Compliance frameworks | GitLab Ultimate | Enforce org-wide branch protection and merge request policies |

## Measuring your posture

[OpenSSF Scorecard](https://github.com/ossf/scorecard) automatically evaluates a repository against around 20 security checks and produces a 0–10 score. Run it in CI and track the score over time:

```yaml
- name: OpenSSF Scorecard
  uses: ossf/scorecard-action@v2.4.4   # pin to a commit SHA in production; do not use @main
  with:
    results_file: results.sarif
    results_format: sarif
    publish_results: true
```

Target Scorecard categories include: Branch-Protection, Code-Review, Signed-Releases, Token-Permissions, Pinned-Dependencies, SAST, and more.

## Common pitfalls

- **Force-push allowed on the default branch** — enables history rewriting and silent code injection.
- **Admin bypass of branch protection** — if admins can bypass protections, the protection is organizational theater, not a technical control.
- **Shared bot account credentials** — a shared PAT for CI that multiple pipelines use is a single point of failure and makes audit logs unattributable.
- **Actions pinned to branch names** — `@main` or `@master` in workflow `uses:` is a supply-chain risk. Pin to SHA.
- **No CODEOWNERS for security-sensitive paths** — security infrastructure (auth, crypto, CI config) must require security review; it should not be mergeable by any repo member.

## Metrics

- OpenSSF Scorecard score trend per repository.
- Percentage of repositories with branch protection fully configured.
- Number of repositories with force-push enabled on default branch (should be zero).
- Number of long-lived PATs in use vs OIDC/workload identity adoption.
- Commit signing coverage (percentage of commits signed on protected branches).

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Default branch protected via branch protection or rulesets (require PR + 1 review); MFA enforced at org level; secret scanning enabled |
| Developing | CODEOWNERS for sensitive paths; status checks required; Dependabot enabled; Actions pinned to digests |
| Defined | Commit signing required; OIDC for CI/CD; Scorecard running in CI; admin bypass disabled; quarterly access review |
| Advanced | Org-wide policy enforced via Allstar or OPA; full audit log retention and alerting on policy violations; provenance tied to signed commits |

---

## Tools[^1]

### Open-source

- [Allstar](https://github.com/ossf/allstar) — OpenSSF GitHub App that continuously enforces security policies (branch protection, MFA, binary artifacts) across an organization's repositories and files issues when violations are detected.
- [gitsign](https://github.com/sigstore/gitsign) — Keyless git commit signing via Sigstore. Signs commits using OIDC identity (GitHub, Google, Microsoft) — no local GPG key management required.
- [OpenSSF Scorecard](https://github.com/ossf/scorecard) — Automated assessment of repository security best practices across roughly 20 checks. Integrates with GitHub Actions and publishes results to the OpenSSF API.
- [Renovate](https://github.com/renovatebot/renovate) — Automated dependency update tool; keeps Actions digests and dependency versions current. Alternative to Dependabot with more configuration flexibility.

### Commercial

- [GitHub Advanced Security](https://github.com/security/advanced-security) — Offered as GitHub Secret Protection (secret scanning with push protection) and GitHub Code Security (CodeQL code scanning, Copilot Autofix, dependency review) integrated into the GitHub PR workflow.
- [GitLab Ultimate](https://about.gitlab.com/pricing/) — Compliance frameworks, protected branches, security policies, and merge request approvals enforced at the group level.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [OpenSSF Scorecard documentation](https://github.com/ossf/scorecard/blob/main/docs/checks.md)
- [GitHub — Hardening security for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [OWASP Top 10 CI/CD Security Risks — CICD-SEC-8: Ungoverned Usage of 3rd Party Services](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [Sigstore gitsign](https://docs.sigstore.dev/signing/gitsign/)
