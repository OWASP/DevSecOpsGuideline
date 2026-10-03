# Security Champions

Security teams are almost always outnumbered by developers — often by ratios of 1:100 or worse. A **Security Champions** program scales application security by embedding security-minded engineers *inside* development teams, rather than relying on a central team to review everything.

A security champion is a developer (or QA, SRE, or product person) on a delivery team who takes on an additional interest in security: they act as the local point of contact, raise security concerns early, help triage findings, and connect their team to the central security function.

## Why a champions program matters

- **Scale** — security expertise reaches every team without hiring an army. At a 1:100 security-to-developer ratio, it is physically impossible for the security team to review every PR, threat model, or design doc. Champions create a distributed security presence.
- **Context** — champions understand their own codebase, deployment environment, and threat surface far better than an outside reviewer. They know which findings matter and which are false positives.
- **Shift-left culture** — security becomes a peer-to-peer norm rather than a top-down mandate from a team developers rarely interact with. Developers listen to each other.
- **Faster feedback** — questions get answered locally (in team standups, Slack channels, PR reviews) instead of queuing for the security team. Fast feedback loops reduce the cost of fixing issues.
- **Two-way information flow** — champions surface real-world friction (tool noise, process bottlenecks) back to the security team, which would otherwise never hear it.

## Building the program

### Recruitment and selection

Recruit volunteers first; intrinsic motivation produces far better champions than nomination. Use this pitch in team channels or all-hands:

> "We're looking for engineers curious about security who want to help their team ship more confidently. As a Security Champion you'll get advanced training, direct access to the security team, and recognition for the security outcomes you drive. Time commitment: roughly 10–15% of your week, protected in your sprint."

When evaluating candidates, prioritize:
- **Curiosity and communication** over technical depth or seniority. A mid-level developer trusted by their peers is more effective than a senior engineer who works in isolation.
- **Peer influence** — a champion nobody talks to cannot shift team culture.
- Aim for at least one champion per product team or squad. Larger teams (10+) may need two.
- Reach across roles: developers, QA engineers, SREs, platform engineers, and technical product managers can all be effective champions with the right support.

### Training and enablement

- Give champions training that goes beyond the baseline all developers receive: threat modeling facilitation, deeper vulnerability classes, tool configuration, and triage methodology.
- Budget **dedicated, protected time** — typically 10–20% of their work week. Champions who are not given time will deprioritize champion work under delivery pressure. This must be agreed with team leads before the program launches.
- Provide direct access to the security team (a shared Slack channel, a weekly office hours slot) so champions can escalate quickly without filing tickets.
- Share internal threat intelligence, past incidents, and post-mortems so champions understand the real-world context behind policies.
- Certifications and external training (OWASP training, security conferences) should be available as a program benefit.

### A champion's typical week

| Time allocation | Activity |
|---|---|
| ~3 hours | Triage and comment on scanner findings in sprint planning or async |
| ~2 hours | Answer security questions from teammates (Slack, PR reviews) |
| ~1 hour | Attend security team office hours or sync |
| ~1 hour | Threat model review or secure design input for an upcoming feature |
| ~1 hour | Champion community of practice, knowledge base updates, or self-study |

This 8–10 hour allocation (10–15% for a full-time engineer) should be reflected in sprint velocity planning.

### Community of practice

- Run a recurring champions community: a shared chat channel for day-to-day questions and a regular video sync (monthly or bi-weekly) for knowledge sharing, policy updates, and collaborative problem-solving.
- Rotate spotlight presentations where champions share what they found and fixed on their team — this spreads knowledge and builds recognition.
- Maintain a shared knowledge base (wiki, runbooks, FAQ) so institutional knowledge is not lost when a champion changes roles or leaves.
- Create a dedicated champions Slack channel where anyone can ask a question and get a real answer within hours — this is the program's most visible daily value.

### Recognition and retention

- Tie champion participation to career growth **explicitly** — performance reviews, promotion criteria, and public recognition at all-hands meetings.
- Create a tiered program (associate champion → champion → senior champion / lead) so there is a visible progression path and a reason to stay engaged.
- Celebrate catches: when a champion spots a critical issue in a design review or triage session, make sure it is acknowledged and credited publicly.
- Annual champion awards (most threats modeled, most findings closed, most knowledge shared) with leadership recognition.

## Handling champion burnout

Champions burn out when they take on too much without organizational backing. Warning signs: missed community calls, declining triage activity, requests to step down.

Prevention:
- Enforce the time allocation — check in with team leads quarterly to ensure sprint planning protects champion hours.
- **Rotate coverage** for champions going on leave so their team is not left uncovered and they do not return to a backlog.
- Provide an escalation path: champions should never be expected to resolve a security problem that requires specialist expertise alone. A clear "call the security team" path removes the burden of being the final answer.
- Recognize and budget for burnout cycles — a champion who steps back after two years is still a net win; celebrate the contribution and recruit a successor.

## Escalation paths

A champion's authority is advisory, not absolute. Define clear escalation levels:

| Situation | Who handles it |
|---|---|
| Team-level security question | Champion answers directly |
| Finding that needs prioritization guidance | Champion + security team sync |
| Critical / high finding that cannot be fixed in-sprint | Champion raises to security team for triage and risk acceptance |
| Suspected active breach or incident | Champion escalates immediately to security team and incident response |
| Disagreement on risk acceptance between team and security | Champion escalates to security engineering lead for arbitration |

## Responsibilities of a champion

| Responsibility | Frequency |
|---|---|
| First point of contact for team security questions | Ongoing |
| Help facilitate threat-modeling sessions and secure design reviews | Per new feature or quarter |
| Triage and prioritize scanner findings before central team escalation | Weekly / per sprint |
| Promote secure-coding standards; shepherd remediation of assigned findings | Ongoing |
| Attend the champions community of practice | Monthly / bi-weekly |
| Report tooling friction and false-positive patterns to the security team | Ongoing |
| Represent the team's security posture in security reviews | Per review cycle |

## Common pitfalls

- **Champions with no time allocated** — champion work competes with sprint commitments and always loses without protected time.
- **No path for escalation** — champions burn out if they are expected to solve security problems their team cannot fix alone with no route to specialist help.
- **Treating champions as a security review bottleneck** — champions should triage and advise, not be required to sign off on every PR. That recreates the bottleneck problem at the team level.
- **Starting too big** — a 50-person champions cohort with no structure, no training schedule, and no community quickly becomes a list of names. Start with 5–10 enthusiastic volunteers, prove the model, then scale.
- **No metrics** — without tracking engagement, defects caught, and threat models run, the program becomes invisible to leadership and risks being cut when budgets tighten.

## Measuring the program

Key metrics to track and report:

| Metric | Why it matters |
|---|---|
| Active champions and team coverage | Shows program reach; flag teams with no champion |
| Threat models facilitated per quarter | Core security activity proxy |
| Findings triaged/closed by champions vs escalated | Champion effectiveness signal |
| MTTR on teams with vs without champions | Business case for the program |
| Training completion rates | Enablement health |
| Developer satisfaction scores (security tooling and support) | Friction and adoption indicator |
| Security issues raised by developers (not scanners) | Ultimate culture shift indicator |

---

## References

- [OWASP Security Champions Guide](https://owasp.org/www-project-security-champions-guidebook/)
- [OWASP Security Champions Playbook](https://github.com/c0rdis/security-champions-playbook)
- [OWASP SAMM — Education & Guidance](https://owaspsamm.org/model/governance/education-and-guidance/)
