# Tracking Maturities

A DevSecOps program is never "done" — it matures. Tracking maturity gives leadership and teams an honest, repeatable picture of where the program stands, where it is improving, and where to invest next. Without it, security spending is hard to justify and progress is invisible. Maturity tracking converts a vague sense of "we're doing security" into an evidence-based conversation about risk and investment.

## Maturity models

Use an established model so assessments are structured, repeatable, and comparable to industry:

- **[OWASP SAMM](https://owaspsamm.org/)** — assesses maturity across five business functions (Governance, Design, Implementation, Verification, Operations) at three levels each. Each level is clearly defined with concrete activities and expected outputs, not vague descriptions. Strong for overall program strategy and executive reporting. SAMM assessments map to business risk, making them effective for communicating with leadership about where to invest.
- **[OWASP DSOMM](https://dsomm.owasp.org/)** — focuses on concrete DevSecOps activities in the pipeline and maps them to maturity levels across dimensions like Static Depth, Dynamic Depth, and Infrastructure. Strong for engineering adoption: every practice is mapped to specific tools and implementation steps. Use DSOMM to track the pipeline and engineering-level maturity.
- **[BSIMM](https://www.bsimm.com/)** — a descriptive model based on what real organizations (finance, healthcare, tech, ISV) actually do, derived from annual data from participating firms. Useful for benchmarking against industry peers: "we are at the median for our sector in code review but below average in attack models."

**How to choose:** SAMM sets strategic direction; DSOMM drives day-to-day engineering adoption. Many programs use both: SAMM for the annual executive report, DSOMM for the engineering team's quarterly review. Add BSIMM when peer-benchmarking is a priority.

## Conducting an assessment

A maturity assessment is only useful if it is honest and consistent. Here is a practical facilitation guide:

### Preparation (1–2 weeks before)

- Select the model and scope (whole organization, one business unit, or one product team).
- Identify participants: security engineers, security champions, senior developers, and product/engineering managers — at least one per business function being assessed.
- Share the model and evidence requirements in advance so participants arrive prepared, not surprised.
- Define what counts as evidence: a policy document alone does not earn credit; a policy plus a passing scan result plus a remediation ticket does.

### Running the session

- Timebox each practice to 10–15 minutes. A full SAMM assessment across five functions typically takes two half-day sessions with the right participants.
- Work through each practice with the group. Present the model's description, ask "do we do this?", then ask "show me the evidence." Score only what can be evidenced.
- Where participants disagree on a score, err toward the lower score and treat the gap as an improvement opportunity. Optimism without evidence hurts the assessment's usefulness.
- Capture the rationale and evidence references for each score, not just the number — this is what makes the next assessment meaningful.

### SAMM scoring — a worked example

SAMM scores each practice on a 0–3 scale. Consider the practice **Secure Build** under Implementation:

- **Score 0** — no defined build process for security; builds run ad-hoc.
- **Score 1** — a defined build process exists; dependency list is known. *Evidence: a `package-lock.json` or `requirements.txt` committed to source control.*
- **Score 2** — build process enforces removal of unneeded dependencies; known vulnerabilities in dependencies are identified. *Evidence: SCA tool configured in CI with passing gate reports.*
- **Score 3** — build process produces an SBOM; all dependencies are vetted and pinned; build provenance is generated and signed. *Evidence: Syft/CycloneDX SBOM attached to each release, cosign provenance attestation in registry.*

Score 1.5 means evidence supports level 1 behaviors and partial evidence for level 2. Do not round up unless the evidence is unambiguous.

## Building a roadmap from the assessment

An assessment without a roadmap is a status report. A roadmap without a roadmap owner is a wish list. After each assessment:

1. **Export all gaps** — every practice scoring below your target level produces a gap.
2. **Prioritize by risk impact** — not all gaps are equal. A missing secrets-scanning practice at score 0 in an active cloud environment is higher priority than a missing fuzzing practice.
3. **Write backlog items** — for each priority gap, create a ticket with: the target score, the evidence needed to reach it, the owner, and the target quarter.
4. **Assign roadmap ownership** — the roadmap needs a named owner (typically the AppSec lead or CISO) who reports on it quarterly.
5. **Gate the next assessment on roadmap progress** — if an item was due last quarter and is not done, that is the first conversation in the next assessment session.

## Metrics that matter

Complement maturity assessments with operational metrics that show whether the program is *working*, not just what practices are *present*:

- **Mean Time to Remediate (MTTR)** — how fast vulnerabilities get fixed, by severity. Critical should be measured in hours to days; high in days to weeks. MTTR that does not improve year-over-year despite scanning investment indicates a workflow or prioritization problem, not a scanning problem.
- **Escape rate** — issues reaching production vs caught earlier in the pipeline. The primary shift-left indicator. A falling escape rate means the program is working; a rising one means risk is accumulating in production.
- **Scan coverage** — percentage of repositories and pipelines with each control type enabled (SAST, SCA, secrets, container, IaC). A security control that runs on 60% of repos has 40% blind spots.
- **Findings backlog age** — age distribution of open findings, by severity. A growing tail of old high-severity findings indicates SLA non-compliance and accumulating risk.
- **False positive rate** — the percentage of flagged issues that are not real vulnerabilities. High rates drive developer fatigue and tool disabling. Track this per scanner and tune aggressively.
- **Developer adoption** — training completion, security champions per team, threat models completed per new feature. Adoption metrics reveal culture, not just tooling.
- **ATT&CK coverage** — detection coverage validated by [Breach and Attack Simulation](../../2-Process/2-7-Operate/2-7-6-Breach-and-attack-simulation.md). Shows what percentage of adversary techniques your detection layer would catch.

## Reporting cadence

Match reporting frequency to audience and decision-making cycle:

| Audience | Cadence | Content |
|---|---|---|
| Engineering teams | Weekly / per-sprint | Scan coverage gaps, MTTR by team, open backlog by age |
| Engineering leadership | Monthly | Trend metrics (escape rate, MTTR), roadmap progress, upcoming SLA breaches |
| CISO / security leadership | Quarterly | SAMM/DSOMM score trend, risk exposure summary, investment asks |
| Board / executive | Annual | Program maturity vs. industry (BSIMM), compliance posture, major incidents and lessons learned |

## Make tracking useful

- **Measure trends, not snapshots** — a SAMM score of 1.8 means little in isolation; a score rising from 1.2 to 1.8 over 18 months means the program is progressing at a healthy pace.
- **Build a roadmap from every gap** — translate gaps into a prioritized, owned improvement plan with target dates. An assessment without a roadmap is a status report, not a management tool.
- **Report to the audience** — leadership wants risk exposure, trend, and investment ROI; engineering teams want actionable, specific detail about what to fix and how. Produce both views from the same underlying data.
- **Avoid vanity and punitive metrics** — total vulnerability count is a vanity metric in a large estate. Ranking individual teams on scanner output incentivizes gaming (suppressing findings, tuning thresholds) rather than fixing. See [Security Culture and Awareness](../../1-People/1-2-Training/1-2-3-Security-culture-and-awareness.md).
- **Close the loop** — every remediated backlog item from an assessment should feed back into the next assessment score. The maturity model is most powerful when it is a living, continuous process.

## Maturity progression

**Starter** — ad-hoc security reviews before major releases. No formal maturity model. Metrics tracked manually in spreadsheets if at all.

**Intermediate** — annual SAMM assessment with a formal report and improvement roadmap. DSOMM used to track pipeline-level controls by squad. Core operational metrics (MTTR, coverage, escape rate) tracked in a dashboard. Metrics reviewed quarterly with engineering leads.

**Advanced** — continuous DSOMM tracking integrated with pipeline data (scan results, gate outcomes, ticket resolution). SAMM assessments semi-annual with board-level reporting. Maturity scores feed OKRs and budget planning. BSIMM comparison used to justify investment against industry peers. All metrics automated, no manual data collection.

## Common pitfalls

- **Optimistic self-assessment** — teams credit themselves for policies they have not implemented. Require artifact evidence for every practice claimed.
- **Assessing but not acting** — an assessment that produces no roadmap, no backlog items, and no follow-up creates cynicism. Assessment without action is worse than no assessment.
- **Chasing the score** — optimizing for a higher maturity number by implementing the easiest practices rather than the most impactful ones.
- **Annual-only tracking** — once-a-year assessments miss drift between cycles. Supplement with continuous operational metrics that update in real time.

---

## Tools[^1]

### Open-source

- [OWASP DSOMM application](https://github.com/devsecopsmaturitymodel/DevSecOps-MaturityModel) — interactive web application for assessing DevSecOps maturity against the DSOMM framework. Supports team-level assessments, progress tracking over time, and export of gap reports. Self-hostable.
- [OWASP SAMM Toolbox](https://owaspsamm.org/assessment/) — official spreadsheet and online tooling for conducting SAMM assessments. Version-controlled assessment templates allow consistent scoring across cycles.

### Commercial

- [Codific SAMMY](https://sammy.codific.com/) — platform for managing SAMM-based maturity assessments at scale, with collaborative scoring, gap analysis, roadmap generation, and trend reporting across multiple teams or business units.

---

### Links

[^1]: Listed in alphabetical order.
