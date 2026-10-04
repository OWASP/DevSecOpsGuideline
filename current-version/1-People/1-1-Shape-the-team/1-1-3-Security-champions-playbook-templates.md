# Security Champions Playbook Templates

Ready-to-copy templates for running a [Security Champions](./1-1-1-Security-champions.md) program. Replace `<placeholders>`, delete what you do not need, and keep the documents in a shared, versioned location. Role boundaries should be consistent with [Roles and Responsibilities](./1-1-2-Roles-and-Responsibilities.md).

## 1. Program charter

```markdown
# Security Champions Program Charter

**Owner:** <AppSec lead>  **Executive sponsor:** <name/title>  **Version/date:** <v1 / YYYY-MM-DD>

## Purpose
Scale application security by embedding trained, volunteer engineers in delivery teams.

## Scope
<Teams / business units covered. Pilot cohort: N champions in M teams.>

## Goals (next 12 months)
1. Every product team has a named champion (target: <N>%).
2. <Threat models per quarter / triage SLA / training completion target>.

## Commitments
- Champions: <10-20>% protected time, agreed with their team lead.
- Security team: training, office hours, direct channel, escalation support.
- Team leads: reserve capacity in sprint planning; include champion work in reviews.

## Authority and limits
Champions advise and triage. They are not required to approve every PR or accept risk on behalf of the organization.

## Escalation
<Link to escalation table and incident contact.>

## Review cadence
Quarterly review with sponsor; annual charter update.
```

## 2. Champion role description

```markdown
# Security Champion - Role Description

**Reports to:** their normal manager (dotted line to <AppSec lead>)
**Time commitment:** <10-20>% of working time, protected in sprint planning

## Responsibilities
- First point of contact for security questions on the team
- Triage scanner findings and prioritize with the team
- Help run threat-modeling sessions for new features
- Share secure-coding guidance and lessons from incidents
- Attend the champions community of practice
- Report tooling friction and recurring false positives
- Escalate per the escalation table

## Not expected to
- Be the sole approver of changes or risk acceptance
- Resolve incidents alone

## Skills we look for
Curiosity, communication, peer trust. Deep security expertise is not required.

## What you get
Training, mentoring, direct access to the security team, visible recognition, and credit in performance reviews.
```

## 3. Nomination and onboarding checklist

```markdown
# Champion Nomination and Onboarding

## Nomination
- [ ] Candidate volunteered or consented to nomination
- [ ] Team lead approved time allocation (<N>%)
- [ ] Candidate added to the champions roster (team, contact, start date)

## Week 1
- [ ] Welcome call with <AppSec lead>; walk through charter and role description
- [ ] Access granted: scanner dashboards, ticket queue, champions channel, knowledge base
- [ ] Buddy (experienced champion or security engineer) assigned

## Month 1
- [ ] Baseline training completed: <course names>
- [ ] Reviewed team's current open findings
- [ ] Introduced to team in standup or retro
- [ ] Added to community-of-practice invite
```

## 4. 30/60/90-day plan

```markdown
# 30/60/90-Day Plan - <Champion name>, <Team>

## Days 1-30: Learn
- [ ] Complete baseline training
- [ ] Review the team's repositories, pipelines, and current scanner configuration
- [ ] Attend two community sessions and one office hours
Outcome: <list of baseline observations about the team's security posture>

## Days 31-60: Contribute
- [ ] Triage the team's open findings with the security team
- [ ] Co-facilitate one threat-modeling session
- [ ] Add one item to the knowledge base
Outcome: <triage backlog reduced to agreed level>

## Days 61-90: Lead
- [ ] Facilitate a threat-modeling session independently
- [ ] Present a spotlight at the community meeting
- [ ] Propose one improvement to team practice or tooling
Outcome: review with manager and <AppSec lead>; agree next-quarter goals
```

## 5. Community meeting agenda

```markdown
# Champions Sync - <date>, <45-60 min>

1. Welcome and actions from last time (5 min)
2. Security team updates: policy changes, tooling, recent incidents (10 min)
3. Champion spotlight: what we found and fixed (10 min)
4. Topic deep dive: <e.g. secrets handling, threat model walkthrough> (15 min)
5. Friction and false-positive round table (10 min)
6. Actions, owners, next meeting (5 min)

Notes: <link>  Recording: <link>
```

## 6. Monthly metrics report

```markdown
# Security Champions Monthly Report - <month/year>

| Metric | This month | Last month | Target |
|---|---|---|---|
| Active champions / teams with a champion | | | |
| Threat models facilitated | | | |
| Findings triaged by champions vs escalated | | | |
| Median time to remediate (teams with champions) | | | |
| Training completion | | | |
| Community attendance | | | |
| Issues raised by developers (not scanners) | | | |

## Highlights
- <notable catches, wins>

## Risks and blockers
- <teams with no champion, time not protected, tooling friction>

## Asks of leadership
- <decisions or support needed>
```

Choose metrics you can collect without extra manual effort; see the full list in [Security Champions](./1-1-1-Security-champions.md#measuring-the-program).

## 7. Offboarding and handover

```markdown
# Champion Offboarding - <Name>, <Team>, <date>

- [ ] Conversation held: reason for stepping back, feedback on the program
- [ ] Successor identified or interim coverage assigned (<name>)
- [ ] Handover note: open findings, ongoing threat models, team-specific context
- [ ] Access updated: channels, dashboards, roster
- [ ] Contribution recognized (announcement, certificate, review input)
- [ ] Alumni status offered (optional): stays in community channel
```

## Common pitfalls

- Copying templates without agreeing protected time with team leads first.
- Collecting metrics nobody reviews; start with three to five.
- Leaving the roster stale, so escalation reaches people who left the team.

## References

- [OWASP Security Champions Guide](https://securitychampions.owasp.org/)
- [OWASP Developer Guide: Security Champions Playbook](https://owasp.org/www-project-developer-guide/release/culture_building_and_process_maturing/security_champions/security_champions_playbook/)
