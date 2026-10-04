# Secure Code Review

Automated scanners find known patterns; human review finds the flaws that need context — a missing authorization check, a business-logic bypass, a trust boundary drawn in the wrong place. Secure code review is the deliberate practice of examining changes for security impact before they are merged. It works best as a **risk-based** activity layered on top of automated tooling, not as a full manual audit of every line.

## When and what to review

Reviewing everything at the same depth does not scale, especially as AI-assisted development increases change volume. Define triggers that raise the depth of review:

| Trigger | Examples | Review depth |
|---|---|---|
| Security-sensitive code | Authentication, session handling, authorization, cryptography, input parsing, deserialization, file upload | Mandatory review by a security champion or trained reviewer |
| Trust-boundary changes | New public endpoint, new third-party integration, new data store, changes to CORS or network exposure | Review against the threat model (see [Threat Modeling](../2-1-Design/2-1-1-Threat-modeling.md)) |
| Build and delivery changes | CI workflows, Dockerfiles, Terraform/Kubernetes manifests, release scripts | Review as production code — a pipeline change can execute with deploy credentials |
| Dependency changes | New or upgraded packages, lockfile diffs | Check provenance, maintainers, and install scripts |
| Large or unusual changes | Very large diffs, generated code, changes by first-time contributors | Split the change or add a second reviewer |
| Everything else | Routine feature work | Standard peer review plus automated gates |

## Review checklists

A short checklist keeps reviews consistent. Anchor it to a recognized baseline rather than inventing one: the [OWASP Top 10](https://owasp.org/www-project-top-ten/) for awareness and the [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/) for verifiable requirements. Keep it to questions a reviewer can answer from the diff:

- **Authentication** — Are credentials, tokens, and session identifiers generated, stored, and invalidated correctly? Is MFA or re-authentication enforced for sensitive actions?
- **Authorization** — Is every new route, query, and object access checked on the server, per object and per function (not just "is the user logged in")? Is the check enforced by default rather than opted into?
- **Input handling** — Is all external input validated at the boundary and encoded for its output context? Are queries parameterized? Are file paths, URLs, and deserialized data constrained?
- **Cryptography** — Are vetted libraries and current algorithms used, with keys from a key manager rather than source code? Is randomness cryptographically secure where it matters?
- **Secrets and data** — Are secrets, tokens, or personal data kept out of code, logs, and error messages?
- **Errors and logging** — Do failures fail closed? Are security events logged without sensitive content?
- **Dependencies** — Is each new dependency necessary, maintained, and the intended package?

## Pull request templates and CODEOWNERS

Make the checklist part of the workflow so it is seen at the right moment:

```markdown
<!-- .github/pull_request_template.md -->
## Security considerations
- [ ] Touches authentication, authorization, crypto, or input parsing
- [ ] Adds or changes an external endpoint, integration, or data flow
- [ ] Adds or updates dependencies (provenance checked)
- [ ] Changes CI/CD, container, or infrastructure configuration
- [ ] Contains AI-generated code that I have read and understood
```

Use CODEOWNERS to route sensitive paths to the right reviewers and enforce it with branch protection (require review from code owners):

```text
# .github/CODEOWNERS
/src/auth/            @org/security-champions
/src/crypto/          @org/security-champions
/.github/workflows/   @org/platform-security
/infra/               @org/platform-security
/AGENTS.md            @org/security-champions
```

Protect the CODEOWNERS file itself with a code owner entry, and require approval from someone other than the author.

## Pairing review with automation

Reviewers should spend attention on what tools cannot judge. Let automation handle the repeatable checks so review comments focus on design and logic:

- Run [SAST](../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md), SCA, and secret scanning on every pull request, with findings shown inline on the diff.
- Treat a clean scan as the *start* of review, not the end. Scanners rarely detect broken access control or business-logic flaws.
- Write custom rules for recurring review findings (for example, "every controller must apply the authorization decorator") so a human comment becomes a permanent automated check.
- Use automated checks to enforce the process itself, such as flagging a pull request that modifies a protected path without the required approval.

## Reviewing AI-generated code

Generated code needs at least the same scrutiny as code from an unknown contributor; see [IDE and AI-assisted development](2-2-2-IDE-and-AI-assisted-development.md) for the underlying risks. In review, pay specific attention to:

- Missing authorization and input validation, which models omit when the prompt does not mention them.
- Deprecated or weak cryptography and string-built queries.
- Dependencies that are unfamiliar or may not exist (hallucinated package names).
- Changes the author cannot explain. If the author cannot describe how it works, it is not ready to merge.
- Modifications to agent instruction files or hooks, which influence future generated code.

AI-assisted review tools can summarize diffs and flag patterns, but they are a supplement: a human with accountability must still approve security-relevant changes.

## Reviewing infrastructure and pipeline changes

Infrastructure-as-code and CI/CD definitions are code with a large blast radius. Review for: new public exposure (open security groups, public buckets), widened IAM permissions, disabled encryption or logging, unpinned third-party actions or images, secrets passed through workflow variables, and triggers that run untrusted pull request code with privileged tokens. Pair with [IaC scanning](../2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md) so misconfigurations are caught before the human sees the diff.

## Training reviewers

Reviewers need to recognize vulnerabilities to catch them. Provide secure coding training aligned to your stack (see [Secure coding](../../1-People/1-2-Training/1-2-1-Secure-coding.md)), run periodic review exercises on deliberately vulnerable code, and feed real findings from incidents and pen tests back into the checklist. Security champions (see [Security champions](../../1-People/1-1-Shape-the-team/1-1-1-Security-champions.md)) act as the escalation point for hard calls.

## Common pitfalls and anti-patterns

- **Checklist theater** — a template that is always ticked without thought. Keep it short and spot-check it.
- **Reviewing only the diff** — a safe-looking change can break an invariant defined elsewhere; reviewers need to follow data flow into callers and callees.
- **Reviewer fatigue on large pull requests** — review quality drops sharply with size. Set a size guideline and split changes.
- **Author approves own change via bot or shared account** — enforce independent approval and dismiss stale approvals on new commits.
- **Relying on scanner green** — absence of findings is not evidence of absence of flaws.
- **No feedback loop** — the same issue found repeatedly in review should become a lint rule, library helper, or training topic.

## Maturity progression

| Level | Practice |
|---|---|
| Starter | Mandatory peer review on the default branch; basic security checklist in the PR template; SAST results visible in pull requests |
| Intermediate | CODEOWNERS on sensitive paths with enforced code-owner review; risk-based triggers defined; reviewers trained on the checklist; IaC and pipeline changes reviewed like application code |
| Advanced | Custom rules derived from review findings; AI-generated changes labeled with enhanced review on sensitive paths; review metrics tracked and reported; periodic review-quality audits |

## Metrics and KPIs

- Percentage of changes to sensitive paths reviewed by a code owner or security champion.
- Security findings caught in review versus found later in testing or production.
- Median time-to-first-review and pull request size (to detect review fatigue).
- Percentage of recurring review findings converted into automated rules.
- Reviewer training coverage.

---

## Tools[^1]

### Open-source

- [Danger JS](https://danger.systems/js/) — Automates pull request hygiene checks (for example, warning when a protected path changes without the expected approvals or tests).
- [reviewdog](https://github.com/reviewdog/reviewdog) — Posts the output of linters and analyzers as inline review comments on pull requests.
- [Semgrep Community Edition](https://github.com/semgrep/semgrep) — Pattern-based static analysis with easy custom rules, suited to turning review findings into automated checks.

### Commercial

- [GitHub Code Security (CodeQL)](https://github.com/security/advanced-security) — Code scanning with inline pull request annotations; CodeQL is free for public repositories.
- [SonarQube Server / Cloud](https://www.sonarsource.com/products/sonarqube/) — Quality gates and security findings reported on pull requests.
- [Snyk Code](https://snyk.io/product/snyk-code/) — SAST with pull request checks and IDE feedback.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
- [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/)
- [GitHub — About code owners](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)
- [IDE and AI-assisted development](2-2-2-IDE-and-AI-assisted-development.md)
- [Static Application Security Testing](../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md)
