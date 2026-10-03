# Frameworks and Standards

No single framework covers all of DevSecOps. Strong programs combine several: one sets the **baseline** of required practices, another measures **maturity**, another drives **engineering adoption** inside the pipeline, and another secures the **supply chain**. This page maps the major frameworks and how they relate to this guideline.

## The frameworks teams use together

### NIST SSDF — Secure Software Development Framework ([SP 800-218](https://csrc.nist.gov/Projects/ssdf))

An outcome-focused baseline of secure-development practices, organized into four practice groups:

- **PO — Prepare the Organization**: establish policies, roles, tools, and environments for secure development before writing a line of code.
- **PS — Protect the Software**: maintain the integrity of source code, third-party components, build processes, and release artifacts. This maps directly to supply-chain security and repository hardening.
- **PW — Produce Well-Secured Software**: apply secure design, coding, testing, and code review practices. The bulk of SAST, SCA, threat modeling, and testing activities live here.
- **RV — Respond to Vulnerabilities**: identify, assess, and remediate vulnerabilities discovered after release, including through external disclosure programs.

SSDF says *what* outcomes to achieve, not *how* to build your pipeline — which makes it well suited to regulated environments and US federal procurement requirements (Executive Order 14028 references SSDF directly). Teams use it as a compliance mapping layer over their existing pipeline.

### OWASP SAMM — Software Assurance Maturity Model ([owaspsamm.org](https://owaspsamm.org/))

Measures and improves security maturity across five business functions: **Governance, Design, Implementation, Verification, Operations**. Each function has practices that are scored at three maturity levels.

SAMM's primary use is the **assessment**: run SAMM against your organization to produce a benchmark, identify gaps, and build a prioritized roadmap. Teams typically run a SAMM assessment annually and use results to set quarterly security program goals. The SAMM toolbox provides a spreadsheet-based assessment tool as well as an online version.

### OWASP DSOMM — DevSecOps Maturity Model ([dsomm.owasp.org](https://dsomm.owasp.org/))

Zooms into concrete technical activities inside CI/CD and assigns them to maturity levels across dimensions like Build, Deploy, Test, and Culture. Where SAMM sets strategic direction, DSOMM drives day-to-day engineering adoption — it tells you *which specific pipeline activity* to implement next.

For example, DSOMM distinguishes between "secrets are scanned in CI" (level 1) and "secrets are scanned pre-commit with automatic block" (level 2) and "secret rotation is automated and verified" (level 3). This specificity makes it a useful benchmark for platform and AppSec teams.

### SLSA — Supply-chain Levels for Software Artifacts ([slsa.dev](https://slsa.dev/))

A graded framework (Levels 1–4) for build integrity and verifiable provenance. Each level adds stronger guarantees about where an artifact came from and how it was built:

- **Level 1**: provenance exists (basic build metadata).
- **Level 2**: provenance is signed; build is hosted on a managed platform.
- **Level 3**: provenance is non-falsifiable; the build environment is hardened.
- **Level 4**: full two-party review; hermetic, reproducible builds.

In practice, reaching SLSA Level 2 with GitHub Actions and Sigstore is achievable for most teams and satisfies most current regulatory and customer requirements. Level 3+ is the target for critical infrastructure software.

### OWASP Top 10 CI/CD Security Risks ([owasp.org](https://owasp.org/www-project-top-10-ci-cd-security-risks/))

The canonical list of risks to the pipeline itself — an important complement to the application-focused OWASP Top 10. Key risks include:

- **CICD-SEC-1**: Insufficient Flow Control Mechanisms (no approval gates, no separation of duties in the pipeline)
- **CICD-SEC-2**: Inadequate Identity and Access Management (overly permissive tokens, no OIDC)
- **CICD-SEC-3**: Dependency Chain Abuse (typosquatting, malicious packages)
- **CICD-SEC-4**: Poisoned Pipeline Execution (PPE) — untrusted code running in a trusted context
- **CICD-SEC-6**: Insufficient Credential Hygiene — long-lived tokens in environment variables or logs

### OWASP Proactive Controls / ASVS / Top 10

Developer-facing security controls, verification requirements, and the best-known web risk list:

- **OWASP Top 10** — the ten most critical web application risks. Use it to prioritize training and testing.
- **OWASP ASVS** — a 200+ item catalog of verifiable security requirements at three levels. Use it to define what "done" means for security in your backlog.
- **OWASP Proactive Controls** — ten defensive techniques every developer should apply. Use it as a quick-start guide for secure coding.

## How they fit together

| Concern | Framework |
| --- | --- |
| Baseline and compliance | NIST SSDF, ISO/IEC 27001, PCI DSS |
| Maturity measurement and roadmap | OWASP SAMM, BSIMM |
| Pipeline engineering adoption | OWASP DSOMM |
| Supply-chain integrity | SLSA, in-toto |
| Pipeline-specific risk | OWASP Top 10 CI/CD |
| Developer controls | OWASP ASVS, Proactive Controls, Top 10 |
| AI/ML risk | OWASP LLM Top 10, NIST AI RMF, ISO/IEC 42001 |

In short: **SSDF = compliance baseline**, **SAMM = strategic maturity**, **DSOMM = engineering adoption**, **SLSA = supply-chain integrity**. This OWASP DevSecOps Guideline sits in the middle — translating these frameworks into concrete, stage-by-stage pipeline controls.

## Regulatory drivers

Several regulations have turned these practices from optional to expected:

- **US Executive Order 14028 / OMB M-22-18** — requires federal software suppliers to attest SSDF compliance and provide SBOMs. Has driven rapid adoption of supply-chain security tooling in commercial software as well.
- **EU Cyber Resilience Act (CRA)** — security requirements, vulnerability handling obligations, and incident reporting for products with digital elements sold in the EU. Covers both software publishers and open-source stewards of "critical" components.
- **PCI DSS v4.0** — requires continuous vulnerability management, penetration testing, and secure development practices. New requirements in v4.0 increase emphasis on application security controls.
- **SOC 2 Type II** — audited against your SDLC for security, availability, and confidentiality. Reviewers examine change management, SAST/DAST evidence, access controls, and incident response.
- **ISO/IEC 27001:2022** — adds supply-chain security (A.5.19–5.22) and secure development lifecycle (A.8.25–8.31) as explicit control objectives.

## Using frameworks without drowning in them

A common failure mode is treating frameworks as compliance exercises to be completed rather than tools to improve outcomes. Practical advice:

- **Pick one maturity model** (SAMM or DSOMM) and run a genuine assessment before shopping for tools. The assessment reveals real gaps; the tools address them.
- **Map your existing controls to SSDF** only if you have a regulatory reason. For most organizations, building a good program first and mapping it to SSDF afterward is more efficient.
- **Use SLSA as an engineering target**, not a compliance checkbox. Start at Level 1, move to Level 2, and measure the journey.
- **Do not maintain parallel compliance artifacts** if you can make your pipeline produce evidence natively (signed build logs, immutable artifact records, policy-as-code reports).

---

## Further reading

- [NIST SSDF (SP 800-218)](https://csrc.nist.gov/Projects/ssdf)
- [OWASP SAMM](https://owaspsamm.org/)
- [OWASP DSOMM](https://dsomm.owasp.org/)
- [SLSA](https://slsa.dev/)
- [OWASP Top 10 CI/CD Security Risks](https://owasp.org/www-project-top-10-ci-cd-security-risks/)
- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework)
- [EU Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
