# Secure Design and Requirements

Threat modeling asks "what can go wrong?"; **secure design and requirements** answer "what must be true for this to be safe?" — *before* implementation begins. Security requirements that are written down become testable, and design decisions made early are far cheaper than retrofits. A whole class of vulnerabilities — the [OWASP Top 10's "Insecure Design"](https://owasp.org/Top10/A04_2021-Insecure_Design/) category — exists precisely because security was never a design input.

## Secure-by-design principles

These principles are not checklists to be stamped once and forgotten — they are design lenses applied throughout every architecture and feature decision:

- **Least privilege** — every component, service, and identity gets only the access it needs, for only the duration it needs it. An overprivileged service that gets compromised becomes a high-blast-radius incident.
- **Defense in depth** — never rely on a single control; assume any one layer can fail. A WAF is not a substitute for input validation; encryption at rest is not a substitute for access control.
- **Fail securely** — errors and edge cases must default to denying access, not granting it. An unhandled exception that returns a `200 OK` with empty data is less dangerous than one that returns a `500` with a stack trace — but both are worse than returning a clean `403`.
- **Minimize attack surface** — fewer features, ports, endpoints, and dependencies mean fewer ways in. Disable or remove anything not required. Every "just in case" API endpoint is a liability.
- **Secure defaults** — the out-of-the-box configuration should be the safe one; security should not require opt-in. Encryption, authentication, and safe error handling should be on by default.
- **Complete mediation** — check authorization on every access to every resource, not just the first request in a session. Cached authorization decisions become stale; privileged routes must validate on every call.
- **Separation of duties** — no single entity should be able to complete a high-risk action alone. Critical operations (e.g., production deploys, key rotation) require two parties.
- **Privacy by design** — build in data minimization and protection from the start. Collect only what you need; retain only as long as required. See [Data Protection](../../3-Governance/3-2-Data-protection.md).

## Security requirements

Principles are not enough — they must be translated into concrete, verifiable requirements that live in the same backlog as functional requirements.

### Using OWASP ASVS

The [OWASP Application Security Verification Standard (ASVS)](https://owasp.org/www-project-application-security-verification-standard/) provides a catalog of hundreds of security requirements organized by category (authentication, session management, cryptography, API, etc.) at three levels:

- **Level 1** — opportunistic; suitable for all applications. Covers basic security hygiene.
- **Level 2** — standard; suitable for applications handling sensitive data. The target for most business applications.
- **Level 3** — advanced; for critical applications (financial, healthcare, infrastructure). Requires formal verification of controls.

Select your ASVS level based on the application's risk classification, then import the relevant requirements into your backlog at project kick-off.

### Abuse cases alongside user stories

For every significant user story, write a corresponding abuse case that describes the same scenario from an attacker's perspective:

> **User story:** "As a customer, I can reset my password using my email address."
>
> **Abuse case:** "As an attacker, I can trigger password resets for accounts I do not own, either locking out legitimate users or using predictable tokens to take over accounts."
>
> **Security acceptance criteria:** Rate-limit reset requests to 5 per hour per account; reset tokens must be cryptographically random (≥128 bits), single-use, and expire in 15 minutes; token delivery channel must be confirmed before issuing.

### Security acceptance criteria in stories

Add a security acceptance criteria section to your story template alongside functional acceptance criteria. This makes security testable by QA and automated tests, not optional.

```
## Security Acceptance Criteria
- [ ] Input is validated server-side (type, length, allowlist where applicable)
- [ ] Output is encoded for the rendering context
- [ ] Authorization check performed for every state change
- [ ] Sensitive fields not logged or included in error responses
```

## Secure design patterns and paved roads

Reusing vetted patterns beats reinventing security per project:

- **Centralized authentication and authorization** — use a shared, audited auth library or identity provider rather than bespoke per-service implementations. Custom auth code is one of the most common sources of high-severity vulnerabilities.
- **Centralized input validation and output encoding** — a shared library that enforces allowlists, maximum lengths, and context-aware encoding eliminates entire vulnerability classes across every consumer.
- **Platform paved road** — golden templates, hardened base images, pre-configured infrastructure modules, and approved building blocks let product teams inherit secure design rather than design it from scratch. The paved road makes the secure choice the path of least resistance.
- **Architecture decision records (ADRs)** — document security trade-offs and rationale in version-controlled ADRs. Future teams need to understand *why* a design is the way it is, not just what it is. An undocumented security constraint is a constraint that gets accidentally removed.

## Design review checklist

Run this at the end of every design phase before implementation begins:

- [ ] Authentication, authorization, and session management fully designed — not left as an implementation detail.
- [ ] Sensitive data classified; encryption strategy chosen for data at rest and in transit.
- [ ] All third-party integrations enumerated; trust level and data sharing scope defined for each.
- [ ] Error handling and logging strategy defined — sensitive data must not appear in logs or error responses.
- [ ] Abuse cases documented for every high-value or high-risk feature.
- [ ] ASVS level selected and applicable requirements imported into the backlog.
- [ ] Threat model created or updated for the design — see [Threat Modeling](2-1-1-Threat-modeling.md).
- [ ] Data flows across trust boundaries documented and reviewed.
- [ ] No hardcoded credentials, keys, or environment-specific values in design artifacts.

## Common pitfalls

- **Delegating auth to "the framework"** without understanding what the framework actually enforces. Frameworks provide primitives; correct design is still required.
- **Designing for the happy path only** — edge cases, error conditions, and concurrent access patterns are where security breaks.
- **ASVS level mismatch** — selecting Level 1 for a system that handles payment data or health records because it is "quicker to implement."
- **No security requirements in the backlog** — security work that isn't tracked doesn't get estimated, prioritized, or completed.
- **Paved road as an island** — building golden templates once and never updating them. Stale templates propagate known vulnerabilities across every new service.

## Industry direction

Regulators and vendors are converging on secure-by-design as a baseline expectation. [CISA's Secure by Design](https://www.cisa.gov/securebydesign) initiative asks software producers to take ownership of customer security outcomes and design products that are secure out of the box. The EU Cyber Resilience Act takes this further by making security-by-design a legal obligation for products with digital elements sold in the EU.

## Maturity progression

| Level | Practice |
|---|---|
| Starting | Security principles referenced in design reviews; ASVS Level 1 requirements added to high-risk stories |
| Developing | Abuse cases written for all significant features; ASVS level selected per application; security acceptance criteria in story template |
| Defined | Paved road with golden templates and shared libraries; ADRs document security decisions; ASVS requirements tracked in backlog |
| Advanced | Automated ASVS requirement generation from threat model output; design reviews gated on completion of abuse cases and security criteria |

## Tools

| Category | Examples |
|---|---|
| Security requirements management | SD Elements (generates tasks from questionnaire), Jira (with security issue types and templates), OWASP ASVS spreadsheet |
| ASVS tooling | OWASP ASVS project (PDF/spreadsheet), OWASP SKF (Security Knowledge Framework — maps ASVS to code examples) |
| Threat modeling (link with design) | OWASP Threat Dragon, Threagile, IriusRisk — see [Threat Modeling](2-1-1-Threat-modeling.md) |
| Architecture diagramming | draw.io (supports DFDs), Mermaid (version-controllable diagrams as code), PlantUML, Structurizr |
| Secure design patterns reference | OWASP Cheat Sheet Series, OWASP Proactive Controls, OWASP ASVS |

---

## Further reading

- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Top 10 — A04 Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)
- [OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/)
- [OWASP Security Knowledge Framework (SKF)](https://owasp.org/www-project-security-knowledge-framework/)
- [CISA Secure by Design](https://www.cisa.gov/securebydesign)
- [EU Cyber Resilience Act](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
