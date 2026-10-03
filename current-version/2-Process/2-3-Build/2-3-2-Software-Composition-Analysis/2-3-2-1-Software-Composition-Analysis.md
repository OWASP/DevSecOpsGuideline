# Software Composition Analysis (SCA)

Modern applications are mostly **third-party code** — open-source libraries and their transitive dependencies often make up 80%+ of a codebase. Software Composition Analysis identifies those components and flags the ones with known vulnerabilities, risky licenses, or signs of malice. Given that supply-chain attacks now rival application bugs as a top risk, SCA is essential.

## The Log4Shell lesson

Log4Shell (CVE-2021-44228, CVSS 10.0) became the defining SCA failure case. The vulnerability was in Log4j — a Java logging library. What made it catastrophic was not the flaw itself, but that:

1. Log4j appeared as a **transitive dependency** in thousands of applications — included by Elasticsearch, Apache Struts, and hundreds of other frameworks that developers chose directly. Teams had no idea they were using it.
2. Exploitation was trivially easy: a single string in any logged input field could trigger remote code execution.
3. Organizations without an accurate **software bill of materials (SBOM)** spent days manually auditing hundreds of applications to determine exposure, while those with SBOM and SCA tooling identified affected services within hours.

Log4Shell is the clearest argument for continuous SCA with full transitive dependency resolution and SBOM-driven inventory.

## What SCA covers

- **Known vulnerabilities (CVEs)** — match dependencies against vulnerability databases (NVD, OSV, GitHub Advisory Database) and maintainer advisories.
- **Transitive dependencies** — the indirect dependencies you never chose explicitly but still ship. These are where most risk hides.
- **License compliance** — detect copyleft (GPL, AGPL) or otherwise incompatible licenses that create legal risk in commercial products.
- **Malicious packages** — detect typosquatting, dependency confusion, and packages exhibiting malicious behavior — increasingly important in the age of [AI-hallucinated dependencies](../../2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md).
- **Outdated components** — surface unmaintained or end-of-life dependencies before they accumulate debt or lose CVE coverage.

## Understanding transitive dependencies

A direct dependency is a package your team explicitly chose. A transitive dependency is everything that package depends on — and everything *those* packages depend on. The depth can be surprising:

```
your-app
└── web-framework@4.2.0          (direct)
    └── http-client@2.1.0        (transitive, depth 1)
        └── xml-parser@1.8.3     (transitive, depth 2)
            └── log4j@2.14.1     (transitive, depth 3) ← vulnerable
```

In this example, your application never imported Log4j, but it ships inside the image and is reachable. SCA tools resolve the full graph; auditing direct dependencies only leaves the depth-2 and depth-3 layers invisible.

## Package URL (PURL) format

SCA tools and SBOMs use **Package URLs (PURLs)** to uniquely identify components across ecosystems:

```
pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1
pkg:npm/%40angular/core@16.0.0
pkg:pypi/requests@2.31.0
pkg:golang/github.com/gin-gonic/gin@v1.9.1
```

PURLs enable unambiguous cross-tool correlation: when an SBOM, a scanner, and a vulnerability database all use the same PURL, findings can be mapped without manual disambiguation.

## Reachability analysis

Most dependency CVEs are never actually exploitable in a given application. Standard SCA flags every known CVE regardless of whether the vulnerable code is called. **Reachability analysis** goes further: it builds a call graph of your application code and determines whether execution can actually reach the vulnerable function.

How it works:
1. Identify the vulnerable function(s) named in the CVE advisory (e.g., `JndiLookup.lookup()` in Log4Shell).
2. Build a call graph from the application's entry points (API handlers, message consumers, scheduled jobs).
3. Determine if any path in the call graph reaches the vulnerable function.
4. If no path reaches it — even though the package is present — the vulnerability is **not reachable** and is deprioritized.

Tools like Endor Labs, Snyk, and Semgrep Supply Chain can reduce actionable SCA findings by 60–85% for typical Java and JavaScript applications using reachability analysis. This dramatically reduces alert fatigue and lets teams focus on genuine risk.

## VEX workflow

Vulnerability Exploitability eXchange (VEX) is a machine-readable statement declaring whether a known CVE affects a specific product:

| VEX status | Meaning |
|---|---|
| `affected` | The vulnerability affects this product version — remediation required. |
| `not_affected` | The vulnerable code is present but not exploitable (e.g., not reachable, feature disabled). |
| `fixed` | The vulnerability was present and has been remediated in this version. |
| `under_investigation` | Impact assessment is in progress. |

**Step-by-step VEX workflow:**
1. SCA scanner flags CVE-YYYY-NNNN in a dependency.
2. Developer or security engineer investigates: is the vulnerable code path reachable? Is the affected feature enabled?
3. If not reachable: create a `not_affected` VEX statement with justification (e.g., "vulnerable HTTP server module never initialized; application uses embedded server").
4. Attach the VEX document to the SBOM (CycloneDX supports inline VEX; OpenVEX is a standalone format).
5. Downstream consumers — customers, operators, compliance teams — consume VEX and discard irrelevant findings automatically.
6. If `under_investigation`: set a resolution deadline (e.g., 5 business days) and assign an owner.

## SCA gate policies

Define clear, enforceable policies at the pipeline gate level:

```yaml
# Example Grype/Dependency-Track gate policy (pseudo-configuration)
policy:
  block:
    - severity: CRITICAL        # CVSS >= 9.0
    - severity: HIGH            # CVSS >= 7.0, with EPSS >= 0.5
    - cisa_kev: true            # Any KEV-listed CVE, any severity
  warn:
    - severity: HIGH            # CVSS >= 7.0 (without EPSS filter)
    - severity: MEDIUM          # CVSS >= 4.0, reachable
  allow:
    - severity: LOW
    - not_reachable: true       # Reachability analysis clears it
    - vex_status: not_affected
```

Apply the block policy to pull requests (new findings only, vs. baseline). Apply the full scan to nightly runs and report to the central dashboard.

## SCA in monorepos

Monorepos introduce additional complexity:
- Multiple language ecosystems in one repository (Go services, Python scripts, Node frontends).
- Shared internal libraries with their own dependency trees.
- Different release cadences per service within the same repo.

Best practices for monorepo SCA:
- Configure the scanner to detect package manifests recursively (`--recursive` in most tools).
- Tag findings with the service or module path so ownership is clear.
- Generate per-service SBOMs, not a single monorepo SBOM — downstream consumers need component scope, not the entire monorepo inventory.
- Use Dependency-Track projects to represent individual services, even if they share a repo.

## Integrating SCA in the pipeline

```yaml
# Example: Grype scan in GitHub Actions
- name: Scan dependencies with Grype
  uses: anchore/scan-action@v3
  with:
    path: "."
    fail-build: true
    severity-cutoff: high
    output-format: sarif
- name: Upload SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: results.sarif
```

- **At every dependency change** (lock file update, PR) — catch new vulnerabilities before they merge.
- **On a schedule** — new CVEs are disclosed daily against existing dependencies; nightly scans catch what wasn't vulnerable at merge time.
- **In the registry** — continuously rescan stored images and artifacts as the vulnerability database grows.
- **At admission/deploy** — policy gates reject artifacts with unresolved criticals (see [Security Gates](../2-3-5-Security-Gates.md)).

## SCA and the supply chain

SCA is tightly linked to the [SBOM](../2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md): the SBOM is the inventory of components, and SCA continuously checks that inventory against new vulnerability intelligence — so a newly disclosed CVE can be mapped to every affected application even after release. This is what enables rapid response to incidents like Log4Shell without manual auditing across hundreds of repositories.

## Common pitfalls and anti-patterns

- **Scanning only at build time** — vulnerabilities disclosed after release require continuous scanning of stored artifacts, not just point-in-time CI scans.
- **No license policy** — finding GPL code in a commercial product after it ships is expensive. Define an approved-license list and enforce it as a gate.
- **Ignoring transitive dependencies** — many exploited vulnerabilities are in transitive, not direct, dependencies. Ensure your SCA tool resolves the full graph.
- **Alert fatigue from untuned gates** — blocking on every medium CVE in a transitive dependency kills developer trust quickly. Tune to reachable, high/critical findings first.
- **Not consuming advisories from maintainers** — NVD lags; maintainer advisories (GitHub Advisory Database, npm advisories, PyPI) often arrive days earlier. Use tools that consume both.
- **No VEX program** — without VEX, every `not_affected` finding must be manually triaged each time it resurfaces. VEX turns that into a one-time documented decision.

## Maturity progression

**Starter** — Run OWASP Dependency-Check or Trivy in CI. Report findings to a dashboard. Establish a baseline of existing vulnerabilities.

**Intermediate** — Gate pull requests on new high/critical findings. Enforce a license allowlist. Schedule nightly scans of existing artifacts. Feed results into a central tracker (Dependency-Track). Produce SBOMs per service.

**Advanced** — Add reachability analysis to cut noise by 60–85%. Produce and publish VEX statements per release. Continuously monitor SBOMs in Dependency-Track with real-time CVE alerting. Track mean time to remediate by severity and measure the exploitable-to-total-findings ratio.

## Metrics and KPIs

| Metric | Target |
|---|---|
| Mean time to remediate (critical CVE, KEV-listed) | < 24 hours |
| Mean time to remediate (critical CVE, non-KEV) | < 7 days |
| % of critical findings with reachability context | > 80% |
| Unlicensed or unapproved-license components | 0 |
| Nightly scan freshness | < 24 hours since last scan per artifact |
| Components at end-of-life | Tracked and on remediation roadmap |
| VEX coverage (findings with a VEX status) | > 90% for critical/high |

---

## Tools[^1]

### Open-source

- [cdxgen](https://github.com/CycloneDX/cdxgen) — Generates CycloneDX SBOMs for many ecosystems (Node, Python, Java, Go, etc.); the easiest way to produce an SBOM that feeds into SCA tooling. Broad language support makes it ideal for polyglot monorepos.
- [Grype](https://github.com/anchore/grype) — Vulnerability scanner for container images and filesystems; fast, pairs naturally with Syft for SBOM-first scanning. Best for teams wanting a lightweight, scriptable CLI scanner.
- [OWASP Dependency-Check](https://owasp.org/www-project-dependency-check/) — Long-established CVE scanner across many languages; easy to add to Maven, Gradle, or CI pipelines. Best for Java/JVM-heavy environments.
- [OWASP Dependency-Track](https://dependencytrack.org/) — Continuous SCA platform that ingests SBOMs and monitors them for new vulnerabilities; best-in-class for SBOM-centric operations and VEX management. The reference platform for SBOM-driven SCA at scale.
- [Trivy](https://github.com/aquasecurity/trivy) — All-in-one scanner for dependencies, images, and IaC; excellent breadth and ease of setup for teams wanting a single tool. Falls short on reachability analysis compared to commercial alternatives.

### Commercial

- [Endor Labs](https://www.endorlabs.com/) — SCA with call-graph reachability; dramatically reduces noise by confirming which vulnerable functions are actually reached. Best for large Java/JavaScript organizations with high false-positive fatigue.
- [Mend (formerly WhiteSource)](https://www.mend.io/) — Comprehensive open-source dependency and license risk management with broad language support. Strong license compliance workflow for legal teams.
- [Snyk Open Source](https://snyk.io/product/open-source-security-management/) — Developer-first dependency vulnerability and license scanning with fix PR automation; strong for developer adoption. Best-in-class developer experience; reachability available for select ecosystems.
- [Sonatype Nexus Lifecycle](https://www.sonatype.com/products/open-source-security-dependency-management) — Component intelligence integrated into the artifact repository; blocks vulnerable components before they enter the build. Best for organizations using Nexus as their artifact registry.

---

### Links

[^1]: Listed in alphabetical order.
