# Regulatory Mapping: CRA, NIS2, and SSDF to Pipeline Controls

> **Disclaimer:** This page is an engineering aid, not legal advice. It summarizes publicly available regulatory text at a high level and maps it to pipeline practices. Scope, applicability, and obligations depend on your product, role (manufacturer, importer, entity type), and national transposition. Confirm interpretations with legal counsel and the official texts linked at the bottom. Dates were checked in October 2026 and may change.

[Frameworks and Standards](./0-3-Frameworks-and-Standards.md) lists the regulations that drive DevSecOps adoption. This page goes one step further: for each obligation, which **pipeline or process control** supports it and which **evidence** the pipeline can produce. The goal is a single set of controls that satisfies several regimes, rather than parallel compliance artifacts.

## Key dates

| Regime | Milestone | Date |
| --- | --- | --- |
| EU Cyber Resilience Act (Regulation (EU) 2024/2847) | Entered into force | 10 December 2024 |
| | Reporting obligations (Article 14) apply | 11 September 2026 |
| | Main obligations (Article 13, Annex I, conformity assessment) apply | 11 December 2027 |
| NIS2 (Directive (EU) 2022/2555) | Applies through **national transposition laws**, which vary by Member State | Check your jurisdiction |
| DORA (Regulation (EU) 2022/2554) | Applies to EU financial entities | 17 January 2025 |
| EU AI Act (Regulation (EU) 2024/1689) | High-risk obligations were postponed by the Digital Omnibus: stand-alone systems to 2 December 2027, AI embedded in regulated products to 2 August 2028 | Verify against the Official Journal; this was reported by secondary sources |
| NIST SSDF (SP 800-218) | v1.1 is final (February 2022); Rev. 1 (SSDF 1.2) was published as an initial public draft on 17 December 2025 | No final version confirmed at time of writing |

## EU Cyber Resilience Act (CRA)

Applies to manufacturers of products with digital elements placed on the EU market. Classes of products and conformity-assessment routes differ; the pipeline controls below are common to all.

| Obligation (CRA reference) | Pipeline or process control | Evidence |
| --- | --- | --- |
| Report actively exploited vulnerabilities and severe incidents: early warning in 24 hours, notification in 72 hours, final report later (Article 14) | Incident response runbook with a CRA reporting step; asset-to-product mapping so you know which products are affected; on-call ownership. See [Vulnerability Management](../2-Process/2-7-Operate/2-7-4-Vulnerability-Management.md) | Tested runbook, tabletop records, report timestamps |
| Products delivered without known exploitable vulnerabilities and with secure-by-default configuration (Annex I, Part I) | [SAST](../2-Process/2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md), [SCA](../2-Process/2-3-Build/2-3-2-Software-Composition-Analysis/2-3-2-1-Software-Composition-Analysis.md), DAST, [security gates](../2-Process/2-3-Build/2-3-5-Security-Gates.md) before release | Scan reports per release, gate decisions, documented exceptions |
| Identify and document components, including an SBOM in a machine-readable format (Annex I, Part II) | Generate an SBOM for every release build. See [SBOM](../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) | SBOM stored with the release artifact |
| Address and remediate vulnerabilities without delay, provide security updates (Annex I, Part II) | Vulnerability triage SLAs; VEX statements to record exploitability decisions; patch release process | Ticket history, SLA metrics, VEX documents, release notes |
| Regular security testing; coordinated vulnerability disclosure policy and contact (Annex I, Part II) | Recurring tests in CI; published disclosure policy. See [VDP and Bug Bounty](../2-Process/2-7-Operate/2-7-5-VDP-and-Bug-bounty.md) | Test history, policy URL, `security.txt` |
| Technical documentation and risk assessment kept up to date (Article 13 and annexes) | Threat modeling at design; living design records. See [Threat Modeling](../2-Process/2-1-Design/2-1-1-Threat-modeling.md) | Versioned threat models and design records |

Notes and uncertainty: the Article 14 reporting channel is ENISA's Single Reporting Platform; one secondary source noted it was not yet live in mid-2026, so check its current status. Exact scope of the SBOM (for example, top-level dependencies as a minimum) should be confirmed against Annex I and Commission guidance.

## NIS2 (Directive (EU) 2022/2555)

Applies to in-scope essential and important entities, not to products as such. Article 21(2) lists minimum risk-management measures. Two points are most relevant to a pipeline:

| Article reference | Pipeline or process control | Evidence |
| --- | --- | --- |
| 21(2)(d) supply chain security, including relationships with direct suppliers and service providers | Dependency and vendor intake review, SBOM requests from suppliers, artifact signing and provenance. See [Artifact Signing and Provenance](../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md) | Supplier assessments, SBOMs received, signature verification logs |
| 21(2)(e) security in acquisition, development and maintenance, including vulnerability handling and disclosure | Secure SDLC controls (SAST, SCA, gates), vulnerability management, disclosure policy | Same as CRA rows above |
| 21(2)(f) policies to assess effectiveness of risk-management measures | Metrics, internal audits, security benchmarking | Dashboards, audit reports |
| 23 incident reporting (early warning 24 hours, notification 72 hours, final report within one month) | Incident response plan with regulator notification step | Runbook, drills |

Some Member States and sector rules (for example Implementing Regulation (EU) 2024/2690 for certain digital service providers) add technical detail. National transposition status varies, so confirm which law applies to you.

## NIST SSDF (SP 800-218)

SSDF is a baseline of outcomes and is the most direct mapping target for pipeline controls. Practice IDs below follow SSDF 1.1; the 1.2 draft adds and renumbers some practices, so re-check when it is finalized.

| SSDF group | Pipeline or process control | Evidence |
| --- | --- | --- |
| PO (Prepare the Organization) | Roles, training, secure toolchain, [security gates](../2-Process/2-3-Build/2-3-5-Security-Gates.md) defined as policy | Policy documents, training records, gate configuration |
| PS (Protect the Software) | [Repository hardening](../2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-4-Repository-Hardening.md), protected branches, signed artifacts, provenance, SBOM | Branch rules export, signatures, attestations, SBOMs |
| PW (Produce Well-Secured Software) | Threat modeling, code review, SAST, SCA, DAST, secrets scanning | Scan results, review records, test reports |
| RV (Respond to Vulnerabilities) | Vulnerability intake, triage, remediation SLAs, root-cause analysis, disclosure program | Tickets, SLA reports, advisories |

## Brief pointers: DORA and EU AI Act

- **DORA** (financial entities): ICT risk management, incident reporting, resilience testing, and ICT third-party risk. Pipeline-relevant overlap is SBOM and supplier evidence, vulnerability management, and testing records.
- **EU AI Act**: obligations for high-risk AI systems include risk management, documentation, and logging. Where your pipeline builds or deploys models, keep model and dataset provenance next to software provenance. See the AI/ML items in [Frameworks and Standards](./0-3-Frameworks-and-Standards.md).

## Collecting evidence from the pipeline

- **Produce evidence automatically** at each build: SBOM, scan reports, gate results, provenance attestation, and signature, stored together and immutable.
- **Keep VEX alongside SBOM** so you can show why a listed vulnerability is not exploitable in your product.
- **Retain by release**, not by tool run, so an auditor or market surveillance authority can retrieve the evidence for any shipped version for the required period (confirm retention requirements with counsel; the CRA ties documentation to the support period).
- **Index evidence by control**, not by regulation, then map controls to regimes in a table like the ones above. See [Compliance Auditing](../3-Governance/3-1-Compliance-Auditing/3-1-1-Compliance-Auditing.md) for continuous compliance and audit-trail practices.

## Common pitfalls

- Treating the CRA as a September 2026 problem only: reporting applies now, but Annex I requirements (SBOM, disclosure policy, update process) need to be built before December 2027.
- Assuming NIS2 or CRA applies uniformly. Check role, product class, and national law.
- Generating an SBOM once and never updating it, or having no VEX process, which leaves every CVE in a component looking exploitable.
- No owner for the 24-hour reporting clock. Define who decides that a vulnerability is actively exploited.
- Mapping to SSDF 1.1 identifiers without a plan for the 1.2 changes.

## Maturity progression

| Level | Characteristics |
| --- | --- |
| Basic | Manual mapping spreadsheet; SBOMs produced ad hoc; disclosure contact exists |
| Intermediate | SBOM and scan evidence stored per release; triage SLAs; tested reporting runbook |
| Advanced | Evidence generated and signed by the pipeline; VEX published; controls mapped once and reused across regimes; continuous audit-ready reporting |

---

## Further reading

- [Cyber Resilience Act (European Commission)](https://digital-strategy.ec.europa.eu/en/policies/cyber-resilience-act)
- [Regulation (EU) 2024/2847 (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2024/2847/oj/eng)
- [NIS2 Directive (EUR-Lex)](https://eur-lex.europa.eu/eli/dir/2022/2555/oj)
- [NIST SSDF project](https://csrc.nist.gov/Projects/ssdf)
- [NIST SP 800-218 Rev. 1 initial public draft](https://csrc.nist.gov/pubs/sp/800/218/r1/ipd)
- [DORA (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2022/2554/oj)
- [EU AI Act (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
