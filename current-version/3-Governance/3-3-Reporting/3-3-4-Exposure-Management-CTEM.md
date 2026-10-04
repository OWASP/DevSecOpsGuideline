# Exposure Management and CTEM

Vulnerability lists describe what is *wrong*; they do not describe what an attacker can actually *reach and exploit*. **Exposure management** widens the lens from individual CVEs to the full set of ways an adversary could compromise the organization: vulnerabilities, misconfigurations, exposed services, over-privileged identities, leaked credentials, and shadow assets. **Continuous Threat Exposure Management (CTEM)** is the program model, introduced by Gartner, for running this as a repeatable cycle rather than a periodic scan-and-report exercise.

CTEM is not a product. It is an operating model that connects discovery, prioritization, validation, and remediation across security, IT, and engineering teams, and it builds directly on the data collected by [ASPM](3-3-3-ASPM.md) and [vulnerability management](../../2-Process/2-7-Operate/2-7-4-Vulnerability-Management.md).

## The five CTEM stages

| Stage | Question it answers | Typical activities |
|---|---|---|
| **1. Scoping** | What matters most to the business? | Define critical services, data, and business processes; agree on what is in scope for the cycle; set ownership |
| **2. Discovery** | What assets and exposures exist in that scope? | Asset and attack-surface discovery; vulnerability, misconfiguration, identity, and secret findings from all sources |
| **3. Prioritization** | Which exposures are most likely to be exploited and most damaging? | Combine exploit likelihood, reachability, asset criticality, and compensating controls |
| **4. Validation** | Can an attacker really exploit this, and do our controls respond? | Attack-path analysis, automated pentest, [breach and attack simulation](../../2-Process/2-7-Operate/2-7-6-Breach-and-attack-simulation.md), manual testing |
| **5. Mobilization** | How do we get the fix done? | Ticketing with owners and SLAs, automated remediation, exception handling, reporting to leadership |

The cycle repeats: the output of mobilization (what was fixed, what was accepted) reshapes the next scope.

## Attack-surface management

**External Attack Surface Management (EASM)** discovers what an outsider can see: domains, subdomains, IP ranges, certificates, exposed cloud storage, forgotten staging environments, and third-party-hosted assets. **Internal and cloud asset discovery** adds workloads, identities, repositories, pipelines, and SaaS applications.

- Seed discovery from known assets (domains, cloud accounts, organizations in source control), then expand using DNS, certificate transparency, and cloud APIs.
- Reconcile discovered assets against the asset inventory. Anything found but not owned is a finding on its own.
- Include the delivery pipeline: source control organizations, CI/CD runners, artifact registries, and their credentials are part of the attack surface (see [CI/CD Pipeline Security](../../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-3-CICD-Pipeline-Security.md)).

## Attack paths, not just findings

Individually moderate issues combine into critical paths: an internet-facing service with a medium-severity flaw, running as a workload with an over-broad role, that can read the production data store. Graph-based analysis models assets, identities, and permissions as nodes and edges so you can ask: *which paths lead from the internet (or a compromised developer laptop) to a crown-jewel asset?*

Fixing a **choke point** that appears in many paths, such as a shared over-privileged role, often removes more risk than patching dozens of isolated CVEs.

## Prioritization signals

No single score is enough. Combine complementary signals:

- **CVSS** — severity of the technical flaw, but not likelihood of exploitation.
- **EPSS** (Exploit Prediction Scoring System, from FIRST) — a probability that a CVE will be exploited in the wild in the next 30 days; useful for ranking large backlogs.
- **CISA KEV** (Known Exploited Vulnerabilities catalog) — confirmed exploitation in the wild; treat entries that affect your assets as top priority with short deadlines.
- **SSVC** (Stakeholder-Specific Vulnerability Categorization, from CERT/CC and adopted by CISA) — a decision-tree approach using exploitation status, technical impact, automatability, mission prevalence, and public well-being impact to arrive at an action such as Track, Track\*, Attend, or Act.
- **Context** — internet exposure, reachability of the vulnerable code, data sensitivity, identity privileges, and existing mitigations.

```text
priority = f(KEV listed, EPSS, exposure, asset criticality, attack-path position, mitigations)
```

Define the formula or decision tree explicitly, document it, and review it with engineering so teams understand why an item is urgent. Use KEV and EPSS data through the vulnerability management platform or ASPM tool rather than manual lookups.

## How CTEM relates to ASPM and vulnerability management

| Discipline | Primary scope | Main output |
|---|---|---|
| [Vulnerability management](../../2-Process/2-7-Operate/2-7-4-Vulnerability-Management.md) | Known vulnerabilities, mostly infrastructure and software components | Patch and remediation queues with SLAs |
| [ASPM](3-3-3-ASPM.md) | Application risk across code, dependencies, containers, pipelines, and runtime | Deduplicated, owned, contextualized application findings |
| Exposure management / CTEM | All exposures across assets, identities, and attack paths, validated for exploitability | A program cycle and prioritized, validated remediation plan |

These are layers, not competitors. The [central vulnerability dashboard](3-3-2-Central-vulnerability-management-dashboard.md) and ASPM supply discovery and contextual findings; CTEM adds business scoping, attack-path reasoning, adversarial validation, and cross-team mobilization on top.

## Validation in practice

Validation separates *theoretical* from *demonstrated* risk and lets you challenge priority both ways.

- **Downgrade** findings proven unexploitable because of network segmentation, authentication, or a compensating control.
- **Upgrade** findings that complete an attack path to critical assets.
- **Test the controls**, not only the vulnerabilities: confirm that detections fire and that blocking controls work, using BAS and purple-team exercises.
- Validate fixes: re-test after remediation to close the item with evidence.

## Mobilization

Prioritization has no value if the work is not done.

- Route validated exposures to the owning team's backlog with a clear fix, a due date derived from priority, and evidence of exploitability.
- Pre-agree **remediation playbooks** and, where safe, automate low-risk changes such as closing a public storage bucket or rotating a credential.
- Provide an **exception process** with expiry dates and compensating controls instead of silent risk acceptance.
- Report exposure trends to leadership in business terms: reduction in validated attack paths to critical assets, not only counts of closed tickets.

## Common pitfalls and anti-patterns

- **Treating CTEM as a tool purchase** — without scoping, ownership, and mobilization, an exposure platform becomes another dashboard.
- **Scope too broad on day one** — start with a defined set of critical services and expand each cycle.
- **CVSS-only prioritization** — ignores exploitation likelihood and context, flooding teams with unexploitable work.
- **Discovery without ownership** — assets found but not assigned to teams stay unresolved.
- **Skipping validation** — unvalidated priorities erode developer trust when "critical" items turn out to be unreachable.
- **Security-only ownership** — mobilization requires engineering and IT leaders to commit capacity and SLAs.
- **Ignoring non-CVE exposures** — misconfigurations, excessive permissions, and leaked secrets often drive real breaches but never appear in a CVE feed.
- **One-time exercise** — exposure changes daily; a yearly assessment is a snapshot, not CTEM.

## Maturity progression

**Starter** — Define critical business services and an owner for each. Maintain an asset inventory and run external discovery against known domains. Prioritize using CVSS plus CISA KEV and fix KEV items on a short SLA.

**Intermediate** — Continuous discovery across cloud, repositories, and pipelines feeding a central platform. EPSS and exposure context added to prioritization. Periodic validation of top findings through pentests or automated testing. Remediation tracked with owner SLAs.

**Advanced** — Full five-stage cycle on a regular cadence with executive sponsorship. Attack-path analysis identifying choke points. Continuous validation through BAS and automated testing. Automated mobilization into engineering workflows. Program outcomes reported as reduced validated exposure to critical assets.

## Metrics and KPIs

- **Asset coverage** — percentage of in-scope assets discovered and mapped to an owner.
- **Unknown asset rate** — newly discovered assets not in the inventory per cycle.
- **KEV remediation time** — time from KEV publication (or detection on your asset) to fix, versus SLA.
- **Validated exposure count** — number of exposures confirmed exploitable, by criticality of affected asset.
- **Attack paths to critical assets** — count and trend of validated paths; should decrease cycle over cycle.
- **Mean time to remediate by priority tier** — measured against SLA, by team.
- **Prioritization accuracy** — share of items flagged urgent that validation confirmed as exploitable.
- **Exception volume and age** — open risk acceptances past their expiry date.

---

## Tools[^1]

### Open-source

- [BloodHound Community Edition](https://github.com/SpecterOps/BloodHound) — Graph-based identity attack-path analysis, originally for Active Directory and Entra ID; also used by defenders to find and remove privilege choke points.
- [Cartography](https://github.com/cartography-cncf/cartography) — CNCF sandbox project that maps cloud and SaaS assets and their relationships into a Neo4j graph, enabling attack-path style queries.
- [Nuclei](https://github.com/projectdiscovery/nuclei) — Template-based scanner for validating exposures and misconfigurations across web, network, and cloud targets.
- [OWASP Amass](https://github.com/owasp-amass/amass) — Attack-surface mapping and external asset discovery.
- [OWASP DefectDojo](https://www.defectdojo.org/) — Aggregation and management of findings from many scanners with deduplication and SLA tracking; a practical base for the discovery and mobilization stages.
- [Prowler](https://github.com/prowler-cloud/prowler) — Cloud security posture assessment for AWS, Azure, GCP, and Kubernetes.
- [Stratus Red Team](https://github.com/DataDog/stratus-red-team) — Cloud attack technique emulation for validating detections and controls.

### Commercial

- [Censys](https://censys.com/) — Internet-scale asset discovery and external attack surface management.
- [Cortex Xpanse](https://www.paloaltonetworks.com/cortex/cortex-xpanse) — External attack surface discovery and management.
- [CrowdStrike Falcon Exposure Management](https://www.crowdstrike.com/en-us/platform/exposure-management/) — Exposure and attack-surface management integrated with an endpoint platform.
- [Pentera](https://pentera.io/) — Automated security validation that safely exploits findings to demonstrate real attack paths.
- [Rapid7 Exposure Command](https://www.rapid7.com/products/command/exposure-management/) — Exposure management combining attack-surface, vulnerability, and cloud findings.
- [Tenable One](https://www.tenable.com/products/tenable-one) — Exposure management platform spanning vulnerability, cloud, and identity data.
- [XM Cyber](https://xmcyber.com/) — Attack-path-based exposure management and continuous exposure validation.

---

### Links

- [EPSS (FIRST)](https://www.first.org/epss/)
- [CISA Known Exploited Vulnerabilities Catalog](https://www.cisa.gov/known-exploited-vulnerabilities-catalog)
- [CISA SSVC](https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc)

[^1]: Listed in alphabetical order.
