# Introduction

The OWASP DevSecOps Guideline explains how to build and operate a secure software delivery pipeline using best practices and a curated, vendor-neutral set of tools. The aim is to help organizations of any size that run a DevOps pipeline introduce security controls without slowing delivery, and to promote a **shift-left** (and increasingly **shift-everywhere**) security culture across the whole development lifecycle.

The ideal goal of this guideline is simple:

> **Detect security issues — whether design flaws or application vulnerabilities — as early and as cheaply as possible, and keep detecting them continuously.**

DevSecOps is about embedding security *into* DevOps. To keep up with the pace of CI/CD, security cannot be a gate at the end; it has to be injected early into how software is designed, written, built, tested, and operated, and then continuously validated in production.

## Why DevSecOps — the cost of waiting

The earlier a vulnerability is found, the cheaper it is to fix. IBM's Systems Science Institute research consistently shows that a defect found in the design phase costs roughly 6× less to fix than one found in implementation, and 100× less than one found in production. These ratios are not exact — they depend on the defect type and system — but the directional truth holds across the industry: late discovery is expensive.

But there is a second, harder cost that the numbers do not fully capture: a vulnerability in production that is *exploited* does not just carry a remediation cost — it carries breach costs, regulatory penalties, reputational damage, customer harm, and executive accountability. The 2020 SolarWinds supply-chain attack, the 2021 Log4Shell disclosure affecting millions of systems, and the 2019 Capital One breach (via a misconfigured WAF/SSRF) all share a common thread: the exploit path existed because security was not a continuous concern throughout delivery.

Traditional security — a penetration test weeks before release, a security team that reviews code on request — cannot keep up with teams that ship multiple times a day. DevSecOps resolves this by automating what can be automated, making security feedback immediate, and building shared ownership so risk decisions happen at the right level.

## How this guideline is organized

This version is structured around the three core pillars of DevSecOps:

- **People** — the teams, roles, culture, and training that make secure delivery possible.
- **Process** — the security activities woven into every stage of the software development lifecycle.
- **Governance** — the oversight, compliance, measurement, and reporting that keep the program accountable and improving.

Under **Process**, the product development lifecycle is divided into seven stages, with security controls mapped to each:

- **Design** — threat modeling, secure-by-design, security requirements.
- **Develop** — pre-commit hooks, secrets management, linting, repository hardening, securing the AI-assisted inner loop.
- **Build** — SAST, SCA, container security, IaC scanning, security gates, and software supply-chain security (SBOM, signing/provenance, pipeline security).
- **Test** — IAST, DAST, mobile app testing, API security, misconfiguration checks.
- **Release** — final sign-off, signed and attested artifacts.
- **Deploy** — admission control, GitOps, progressive delivery.
- **Operate** — cloud-native runtime security, logging and monitoring, pentesting, vulnerability management, disclosure programs, and breach-and-attack simulation.

You can customize these stages to match your own SDLC and architecture, and add automation progressively as your maturity grows.

## What DevSecOps is NOT

Understanding the common misconceptions is as important as knowing the definition:

- **DevSecOps is not "security team in the pipeline"** — adding security engineers to approve every PR does not scale. The goal is to give developers the tools, training, and context to make security decisions themselves, with the security team acting as an enabler and escalation path, not a gatekeeper.
- **DevSecOps is not tool procurement** — buying a SAST, SCA, and DAST tool without a triage process, clear ownership, and remediation SLAs creates alert fatigue and false confidence. Tools are enablers; process and culture are the program.
- **DevSecOps is not a one-time project** — there is no "done." The threat landscape, your architecture, your dependencies, and your regulatory obligations all change continuously. DevSecOps is a continuous practice, not a migration.
- **DevSecOps is not compliance** — passing an audit is a floor, not a ceiling. Compliance frameworks describe minimum bars against known risks; a real-world adversary does not follow the framework. Design for adversaries, not just auditors.
- **DevSecOps is not just CI/CD** — the pipeline is important, but threat modeling happens at design, culture happens in teams, runtime security happens in production, and vulnerability disclosure happens at the boundary with the outside world. The pipeline is one layer of a much broader system.

## A note on the pipeline itself

CI/CD is a powerful entry point for security automation, but the build and automation tooling is also part of your attack surface. Compromised pipelines, leaked tokens, and poisoned dependencies are now among the most damaging attack vectors — the SolarWinds, Codecov, and XZ Utils incidents all illustrate how the build and supply chain can be abused to reach production at scale. This guideline therefore treats **securing the pipeline** as a first-class concern alongside securing the application.

## How to use this guideline

Different audiences will find different entry points most useful:

**If you are a developer or engineer:**
Start with the [Develop](../2-Process/2-2-Develop) stage, specifically pre-commit hooks and secrets management — the controls you can implement in your own workflow today. Then read the [Build](../2-Process/2-3-Build) stage for what your CI pipeline should enforce. Use the [Threat Modeling](../2-Process/2-1-Design/2-1-1-Threat-modeling.md) page when you are designing a new feature or service.

**If you are a security engineer or AppSec lead:**
Start with the [Overview](0-2-Overview.md) for a full pipeline view, then use the [Frameworks and Standards](0-3-Frameworks-and-Standards.md) page to map this guideline to your regulatory or maturity framework requirements. Use the [Governance](../3-Governance) section to build a reporting and measurement program.

**If you are an engineering manager or CISO:**
Start with the [Maturity levels](#maturity-levels--where-to-start) table below and the [Tracking Maturities](../3-Governance/3-3-Reporting/3-3-1-Tracking-maturities.md) page. The [People](../1-People) section covers the organizational structures (security champions, roles) that make the program sustainable.

## Common anti-patterns to avoid

- **Security as a gate at the end** — running a pentest or DAST scan as the sole security activity before release does not scale, finds issues too late, and creates a bottleneck. Gates are necessary but not sufficient.
- **Tool sprawl without process** — buying or deploying many scanners without a clear triage, ownership, and remediation process generates noise and alert fatigue that causes teams to ignore findings entirely.
- **Centralized security ownership** — a small security team that "owns" security and must review everything becomes a bottleneck and a single point of failure. Shared ownership, supported by tooling and champions, is the goal.
- **Treating compliance as security** — passing an audit is not the same as being secure. Compliance is a floor, not a ceiling; design for real-world adversaries, not just checkbox controls.
- **Ignoring developer experience** — security tooling that is slow, noisy, or hard to use gets disabled or routed around. Developer experience is a security concern.

## Maturity levels — where to start

| Stage | What to focus on |
|---|---|
| Starting out | Secrets scanning in CI, SCA for known CVEs, basic branch protection, OWASP Top 10 awareness training |
| Developing | SAST in pull requests, IaC scanning, security gates on high/critical findings, security champions program |
| Maturing | Container hardening, SBOM generation, threat modeling, DAST, vulnerability management SLAs |
| Advanced | Supply-chain signing and provenance (SLSA), ASPM, BAS, runtime detection-as-code, AI/ML security |

## Where to start

- [OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/) lists the top security controls every developer should implement while coding.
- [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/model/) helps you decide what to prioritize according to your maturity level.
- The [Frameworks and Standards](0-3-Frameworks-and-Standards.md) page maps how SSDF, SAMM, DSOMM, and SLSA fit together with this guideline.
- The [Overview](0-2-Overview.md) page lists a recommended progression of controls to introduce into a pipeline.

If you need earlier editions, see the [old-versions](../../old-versions/) directory.
