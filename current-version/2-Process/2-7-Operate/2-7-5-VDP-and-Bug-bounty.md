# Vulnerability Disclosure and Bug Bounty

No matter how strong your pipeline, external researchers and users will find issues you missed. The question is whether they have a **safe, clear way to tell you** — or whether they post it publicly, sell it, or stay silent. A Vulnerability Disclosure Program (VDP) and, optionally, a bug bounty program turn the outside security community into an extension of your defenses.

## Vulnerability Disclosure Program (VDP)

A VDP is the baseline: a published policy that invites anyone to report vulnerabilities and tells them how. It does not require financial incentives — it requires clarity and commitment.

### Core components of a VDP

**`security.txt`** — publish a standardized [security.txt](https://securitytxt.org/) file at `/.well-known/security.txt` so automated tools and researchers can find your contact and policy:

```
Contact: mailto:security@yourcompany.com
Expires: 2026-12-31T00:00:00.000Z
Acknowledgments: https://yourcompany.com/security/hall-of-fame
Policy: https://yourcompany.com/security/vulnerability-disclosure-policy
Preferred-Languages: en
```

**Clear policy** — a published disclosure policy must address:
- Scope: which systems, domains, and products are in scope and explicitly out of scope.
- How to report: encrypted email (PGP key), web form, or platform (HackerOne, Bugcrowd).
- What to expect: acknowledgment SLA, validation SLA, disclosure timeline.
- What is prohibited: destructive testing, social engineering, accessing others' data, DoS.

**Safe harbor** — commit explicitly not to pursue legal action against researchers who discover and report vulnerabilities in good faith within the policy scope. Without safe harbor, researchers avoid reporting for fear of prosecution. Safe harbor is non-negotiable for a functional VDP.

**Coordinated disclosure** — work with the reporter on a fix timeline before public disclosure. Industry standard is 90 days (Google Project Zero model). Communicate progress throughout. If you need more time, request it explicitly and explain why.

**Triage SLAs** — define and meet response commitments:

| Stage | Target SLA |
|---|---|
| Initial acknowledgment | 24–48 hours |
| Validation (is it real?) | 5 business days |
| Severity assessment | 5 business days |
| Status update cadence | Every 14 days until resolved |
| Resolution notification | Within 7 days of fix deployment |

Nothing discourages researchers faster than silence. A VDP with poor triage is worse than no VDP — it creates expectations and then breaks them.

### Legal and regulatory considerations

VDPs are increasingly expected or required:
- [CISA](https://www.cisa.gov/resources-tools/resources/guidance-coordinated-vulnerability-disclosure-processes) recommends all US federal agencies maintain a VDP; many civilian agencies are required to.
- [ISO/IEC 29147](https://www.iso.org/standard/72311.html) covers vulnerability disclosure processes; [ISO/IEC 30111](https://www.iso.org/standard/69725.html) covers vulnerability handling.
- The EU Cyber Resilience Act will require coordinated vulnerability disclosure for products with digital elements.
- Many enterprise procurement processes now require suppliers to have a published VDP.

## Bug bounty programs

A bug bounty program adds **financial incentives** on top of a VDP, attracting more researchers and motivating them to pursue harder-to-find vulnerabilities. It is a significant step up in maturity — only run one once you can triage and remediate reliably at volume.

### Readiness prerequisites

Before launching a bug bounty:
- A working VDP with demonstrated SLA adherence.
- A vulnerability management system capable of handling a sustained inflow of reports.
- Dedicated triage capacity (internal security team or managed triage from the platform).
- Clear scope definitions and reproducible test environments for researchers.
- Legal review of the safe harbor language.

### Program design

**Private vs public** — start with a private program (invited, vetted researchers; controlled volume) before going public. A private program lets you calibrate triage capacity and scope before being exposed to the full researcher community.

**Scope and reward table** — match rewards to severity and business impact:

| Severity | Example | Reward range |
|---|---|---|
| Critical | Authentication bypass, RCE, data exfiltration | $5,000–$30,000+ |
| High | BOLA/IDOR affecting multiple accounts, stored XSS | $1,000–$5,000 |
| Medium | CSRF, reflected XSS, rate-limit bypass | $200–$1,000 |
| Low / informational | Missing headers, clickjacking, self-XSS | $0–$200 or recognition only |

Reward levels vary significantly by industry and organization. Financial services and infrastructure companies typically pay more than consumer applications for equivalent severity.

**Acknowledgment program** — a public hall of fame for researchers who report valid vulnerabilities, even without monetary rewards, is a meaningful incentive for many researchers.

### Managing researcher relationships

- Respond respectfully and promptly. Researcher communities are small and word travels fast.
- When you dispute a finding, explain clearly and provide technical detail.
- Pay promptly once a finding is validated and fixed.
- Consider giving bonus rewards for particularly creative or impactful findings.

## Maturity progression

**Starter** — Publish a `security.txt` and a simple VDP page with an email contact. Commit to 48-hour acknowledgment and 90-day disclosure. Designate an internal owner to handle reports.

**Intermediate** — Migrate to a managed VDP platform for structured intake, triage tracking, and researcher communication. Formal scope definition. Documented triage SLAs. Acknowledgments page for researchers.

**Advanced** — Private bug bounty with invited researchers. Dedicated triage (internal or managed). Reward table tied to severity and impact. VDP/bounty findings feed the vulnerability management pipeline and ASPM. Regular scope reviews to add new assets. Public bug bounty once private program is stable.

## Common pitfalls and anti-patterns

- **VDP with no safe harbor** — researchers will not report without legal protection. A policy that says "don't hack us" but offers no explicit safe harbor is not a VDP.
- **Slow or silent triage** — researchers who submit reports and receive no response for weeks will escalate publicly. SLA adherence is reputation management.
- **Scope too broad too soon** — a first VDP or bounty that covers everything creates unmanageable volume. Start narrow (e.g., one public-facing product) and expand as capacity allows.
- **Bug bounty as a replacement for internal security** — a bounty finds bugs; it does not fix the root causes. Without a strong internal security program, you will remediate the same classes of vulnerability repeatedly.
- **Not fixing bounty findings** — a bounty program that pays researchers but leaves findings unpatched for months destroys credibility with researchers and fails to improve security.

## Metrics and KPIs

- **Triage SLA adherence rate** — percentage of reports acknowledged and validated within SLA; target > 95%.
- **Valid report rate** — percentage of submitted reports that are confirmed valid vulnerabilities; low rate may indicate unclear scope or poor researcher targeting.
- **Mean time to remediate bounty findings** — by severity; compare to internal finding MTTR.
- **Total valid reports per quarter** — indicates researcher engagement and program health.
- **Critical/high findings from external researchers** — vulnerabilities found externally that were missed internally; a high number indicates gaps in the internal security program.

---

## Tools[^1]

### Open-source

- [security.txt](https://securitytxt.org/) — RFC 9116 standard for a machine-readable security contact and disclosure policy file; minimal investment, immediate benefit.

### Commercial

- [Bugcrowd](https://www.bugcrowd.com/) — Crowdsourced bug bounty and VDP platform; managed triage services available; strong researcher community across web, mobile, and IoT.
- [HackerOne](https://www.hackerone.com/) — Vulnerability disclosure and bug bounty platform; largest researcher community; strong tooling for program management, SLA tracking, and integrations with Jira and Slack.
- [Intigriti](https://www.intigriti.com/) — European-based bug bounty and VDP platform; GDPR-aligned; strong European researcher community; growing global presence.
- [Synack](https://www.synack.com/) — Managed crowdsourced security with a vetted, full-time researcher pool; higher cost, higher signal-to-noise ratio; popular with financial services and government.

---

### Links

[^1]: Listed in alphabetical order.
