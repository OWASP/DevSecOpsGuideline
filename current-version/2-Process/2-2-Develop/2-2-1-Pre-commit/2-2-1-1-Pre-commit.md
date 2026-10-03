# Pre-commit

Pre-commit hooks are the **earliest possible shift-left gate** — they run on the developer's machine *before* code is even committed, giving feedback in seconds rather than minutes (CI) or days (review). Catching a leaked secret, a syntax error, or an obvious vulnerability here is the cheapest fix in the entire lifecycle.

## What pre-commit hooks are

Git supports client-side hooks that fire on events like `commit`, `push`, and `merge`. Managing these by hand across a team is painful and inconsistent: hooks live in `.git/hooks/`, which is not committed to the repository, so every developer's environment diverges over time.

The widely adopted [pre-commit](https://pre-commit.com/) framework solves this. It installs, versions, and runs hooks consistently by reading a `.pre-commit-config.yaml` file that *is* committed to the repo. Every developer runs the same checks against the same tool versions, and onboarding is a one-time `pre-commit install`.

```bash
# One-time setup per developer
pip install pre-commit
pre-commit install          # installs the git hook
pre-commit install --hook-type pre-push   # optional: also run on push
```

## A practical `.pre-commit-config.yaml`

```yaml
# .pre-commit-config.yaml
repos:
  # Secret scanning — highest priority, runs first
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks

  # General file hygiene
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: detect-private-key
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'master']

  # Python SAST
  - repo: https://github.com/PyCQA/bandit
    rev: 1.7.9
    hooks:
      - id: bandit
        args: ['-c', 'pyproject.toml']
        files: '\.py$'

  # Semgrep for polyglot SAST (fast subset of rules)
  - repo: https://github.com/returntocorp/semgrep
    rev: v1.x.x
    hooks:
      - id: semgrep
        args: ['--config', 'p/default', '--error']
```

Pin `rev` values to exact tags or SHAs, not `latest`, to make hook execution reproducible and to avoid supply-chain attacks via mutable tags.

## What to run at pre-commit

Keep hooks **fast** — hooks that exceed 10–15 seconds get bypassed or disabled. Optimize for signal-to-noise and speed:

| Check | Why | Typical duration |
|---|---|---|
| Secret scanning | Blocks credentials before they enter history — the most important hook | < 2s |
| Detect private key | Catches PEM/key files committed accidentally | < 1s |
| Large file blocking | Prevents binaries bloating git history | < 1s |
| YAML/JSON/TOML validation | Catches broken config files before they reach CI | < 1s |
| Security linting (Semgrep/Bandit) | Fast rule-based SAST for the most common vulnerability patterns | 2–10s |
| Code formatting (Black, Prettier) | Eliminates style noise in code review | 2–5s |
| No-commit-to-branch | Prevents accidental direct commits to protected branches | < 1s |

Avoid running full test suites, slow SAST scans, or network-dependent checks at pre-commit. Those belong in CI.

## Running hooks in CI

Client-side hooks improve developer experience but are **not a security control on their own** — any developer can skip them with `--no-verify`. Always mirror the same checks server-side in CI:

```yaml
# GitHub Actions example — mirrors pre-commit checks
- name: Run pre-commit hooks
  uses: pre-commit/action@v3.0.1
  env:
    SKIP: no-commit-to-branch   # skip branch-protection hooks in CI context
```

This creates a two-layer model:
- **Pre-commit (local):** fast feedback for the developer, zero round-trip time.
- **CI (server-side):** authoritative, un-bypassable enforcement.

A finding blocked in CI but caught locally first costs nothing. A finding that reaches CI first costs a pipeline run and a developer context-switch.

## Keeping hooks up to date

Hook versions drift. Run `pre-commit autoupdate` periodically (or as a scheduled CI job) to pull the latest revisions of each hook:

```bash
pre-commit autoupdate
git commit -am "chore: update pre-commit hook versions"
```

## Common pitfalls

- **Skipping with `--no-verify`** — a common response to slow or noisy hooks. Fix the noise; don't suppress the gate. If developers reach for `--no-verify` routinely, the hooks are misconfigured.
- **Not pinning hook versions** — using `rev: main` or a branch means hook behavior silently changes. Pin to a tag or SHA.
- **Running too much** — hooks that take 30+ seconds drive developers to bypass them. Keep pre-commit under 15 seconds total.
- **Treating pre-commit as the only gate** — it is not. Enforce the same checks in CI.
- **No onboarding documentation** — if `pre-commit install` is not in the project README or onboarding guide, new developers skip it.

## Metrics

- Percentage of team members with hooks installed (measure via CI — jobs that skip hooks without explanation can be flagged).
- Number of secrets blocked at pre-commit vs caught in CI or later (pre-commit blocks should be the large majority).
- Hook execution time trend — rising times indicate hook bloat and predict bypass rates.

## Maturity progression

| Level | Practice |
|---|---|
| Starting | `pre-commit` installed with secret scanning and basic file hygiene; developers install manually |
| Developing | Standard `.pre-commit-config.yaml` committed to all repos; onboarding automates `pre-commit install`; mirrored in CI |
| Defined | Hook versions pinned and auto-updated by a scheduled job; security linting (Semgrep) included; metrics tracked |
| Advanced | Org-wide hook baseline enforced via a shared config; violations in CI block merge; coverage tracked per repo |

---

## Tools[^1]

### Open-source

- [Husky](https://typicode.github.io/husky/) — Git hooks manager popular in JavaScript/Node projects. Hooks are defined in `package.json` or `.husky/`. Works well with lint-staged for running checks only on staged files.
- [Lefthook](https://github.com/evilmartians/lefthook) — Fast, polyglot Git hooks manager written in Go. Supports parallel hook execution and per-file filtering. Good alternative to `pre-commit` for multi-language monorepos.
- [pre-commit](https://pre-commit.com/) — The most widely adopted multi-language framework for managing pre-commit hooks. Declarative YAML config, plugin ecosystem, CI integration, autoupdate support.
- [lint-staged](https://github.com/lint-staged/lint-staged) — Runs linters only on git-staged files. Often paired with Husky to keep pre-commit fast by scoping checks to changed files only.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [pre-commit documentation](https://pre-commit.com/)
- [OWASP Cheat Sheet — Vulnerable Dependency Management](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)
- [Gitleaks — secret scanning hook](https://github.com/gitleaks/gitleaks)
