# Roles and Responsibilities

DevSecOps works only when security is a **shared responsibility**. That does not mean everyone does everything — it means each role has clear, explicit security duties and the boundaries between them are understood. Ambiguity ("I thought security owned that") is where risk accumulates.

## Core roles and their security duties

### Developers

Developers are the primary consumers of shift-left tooling and the first line of defense for application security:

- Write secure code and apply the [OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/).
- Run pre-commit hooks and IDE security plugins; fix findings on their own code before opening a PR.
- Participate in threat modeling sessions and secure code review for their features.
- Write security acceptance criteria alongside functional acceptance criteria.
- Review AI-generated code with the same scrutiny as hand-written code.

### Security Champions

Embedded developers who act as the local security point of contact — see [Security Champions](1-1-1-Security-champions.md) for the full program description. Their unique value is combining the developer's context with security expertise: they can translate between the security team's concerns and the team's engineering realities.

### AppSec / Security Engineers

Own the application security function:

- Define security requirements, policies, and gate thresholds.
- Own and tune the AppSec tooling (SAST, DAST, SCA, IAST, secrets scanning).
- Support triage — help developers distinguish real vulnerabilities from false positives.
- Run or support threat modeling for high-risk features and new architectures.
- Conduct security code reviews and provide consultation.
- Design and deliver security training (with the champions network as a force multiplier).
- Track and report on the security posture of the application portfolio.

### DevSecOps / Platform Engineers

Build and maintain the secure **paved road** — the infrastructure that makes security the default:

- Harden CI/CD templates: enforce least-privilege tokens, pin dependencies, add security scanning as a standard step.
- Build and maintain approved, hardened golden base images for containers and VMs.
- Provide reusable, security-compliant IaC modules (Terraform modules, Helm charts) so product teams cannot easily misconfigure infrastructure.
- Maintain the self-service developer portal that surfaces security tooling as a first-class capability.
- Monitor the pipeline itself as an attack surface and apply the [OWASP Top 10 CI/CD](https://owasp.org/www-project-top-10-ci-cd-security-risks/) hardening checklist.

### SRE / Operations

Own runtime security posture and the reliability of security controls in production:

- Monitor for security events and anomalies; operate the SIEM and alerting.
- Own incident response runbooks and lead security incident response for runtime events.
- Ensure backup, recovery, and availability controls function correctly.
- Feed production threat intelligence (active exploits, runtime anomalies) back to the engineering and AppSec teams.

### Security Architects

Define the security structure that product teams build on:

- Design reusable secure design patterns (authentication, authorization, cryptography, API security).
- Threat-model high-risk systems and new architectural domains.
- Set technical security standards and ensure they are captured in the paved road.
- Review and sign off on major architectural decisions with significant security implications.

### Product Owners / Managers

Own the business risk decisions:

- Prioritize security work in the backlog alongside feature work — security stories must be estimated, scheduled, and tracked like any other work.
- Accept or escalate residual risk with awareness of the business consequences.
- Ensure abuse cases and security acceptance criteria are part of story definition of done.

### GRC / Compliance

Bridge security and regulatory obligations:

- Map pipeline controls to compliance frameworks (SSDF, PCI DSS, SOC 2, ISO 27001).
- Manage audit evidence collection and liaise with auditors.
- Track and review risk acceptance decisions; ensure exceptions have time-bound remediation plans.
- Monitor the regulatory landscape for changes that affect control requirements.

### CISO / Security Leadership

Accountable for the overall security posture:

- Set security strategy, program goals, and risk appetite.
- Fund security work, including training, tooling, and champion program time allocations.
- Communicate security posture and risk to executive and board stakeholders.
- Hold engineering leadership accountable for remediation SLAs.

## Platform engineering and the paved road

Modern programs lean heavily on **platform engineering**: instead of asking every team to assemble security tooling themselves, a platform team provides golden paths — pre-hardened pipelines, templated IaC, vetted base images, and built-in scanning. Security becomes the default behavior of the platform rather than a checklist each team must remember.

This approach scales security coverage dramatically without scaling the security team. A team of five platform engineers can raise the security baseline for hundreds of product developers by building and maintaining the right defaults.

The paved road only works if it is kept current. Assign clear ownership for updating golden templates when new vulnerabilities, tooling updates, or policy changes require it.

## The emerging AI/ML role

As AI moves into the SDLC, a new specialization is appearing: **DevSecOps for AI/ML pipelines** (sometimes "MLSecOps"). These engineers secure the model lifecycle:

- Training data integrity — provenance, poisoning detection, access controls.
- Model provenance and AI-BOMs — tracking what model, what weights, what training data.
- Securing the inference path — input validation, output filtering, prompt injection defenses.
- Scanning AI-generated code and the supply chain of models and datasets.

See [AI Governance and Risk](../../3-Governance/3-4-AI-Governance-and-Risk.md) for the full treatment.

## A simple RACI view

A lightweight RACI matrix per activity prevents gaps and surfaces ownership disputes before they become incidents:

| Activity | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Fix SAST finding in app code | Developer | Eng. manager | AppSec, Champion | Security lead |
| Tune scanner / define gates | AppSec | AppSec lead | Dev teams, Platform | Leadership |
| Harden CI/CD pipeline | Platform eng. | Platform lead | AppSec | Dev teams |
| Runtime incident response | SRE | SRE lead | AppSec, Dev | Leadership |
| Risk acceptance / exception | Product owner | CISO | AppSec | Auditors, GRC |
| Threat model new feature | Champion + AppSec | Eng. manager | Security architect | Product owner |
| Security training delivery | AppSec | CISO | Champions | All developers |
| Compliance audit evidence | GRC | CISO | AppSec, Platform | Legal |

Keep it lightweight and revisit it as the program matures or when ownership disputes arise.

## Common pitfalls

- **"Security's job"** — when developers believe security is someone else's responsibility, they defer findings, skip threat modeling, and route around controls.
- **AppSec as the only triage point** — every finding routed through the AppSec team creates a bottleneck that scales as O(number of findings). Champions and automated prioritization must handle the first tier.
- **Platform team isolated from security** — a platform team that builds without AppSec input produces paved roads with security gaps baked in and replicated across all consumers.
- **GRC and engineering in silos** — compliance requirements that are not translated into engineering controls get evidenced with screenshots rather than automated verification.

---

## Further reading

- [OWASP SAMM](https://owaspsamm.org/)
- [OWASP DevSecOps Maturity Model (DSOMM)](https://dsomm.owasp.org/)
- [Team Topologies — platform teams](https://teamtopologies.com/)
- [CISA Secure by Design — shifting responsibility](https://www.cisa.gov/securebydesign)
