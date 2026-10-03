# Secure Coding Training

Most vulnerabilities are introduced while code is being written. The cheapest place to prevent them is in the developer's head — which makes **secure coding training** one of the highest-leverage investments in a DevSecOps program. The goal is not to turn every developer into a security expert, but to give them the awareness, patterns, and reflexes to avoid the common, costly mistakes.

## What to teach

### Core web and application risk

- **The OWASP Top 10** — [owasp.org/www-project-top-ten](https://owasp.org/www-project-top-ten/) — covers the ten most critical web application risks. Every developer writing server-side code should understand injection, broken access control, cryptographic failures, and insecure design.
- **The relevant variant for your stack** — [OWASP API Top 10](https://owasp.org/www-project-api-security/) for API developers, [OWASP Mobile Top 10](https://owasp.org/www-project-mobile-top-10/) for mobile engineers, [OWASP LLM Top 10](https://owasp.org/www-project-top-10-for-large-language-model-applications/) for teams building AI-powered features.

### Security requirements and verification

- **OWASP ASVS** — [owasp.org/www-project-application-security-verification-standard](https://owasp.org/www-project-application-security-verification-standard/) — a concrete checklist of what "secure" means for authentication, session management, input validation, cryptography, API security, and more. Use it as a training curriculum and as the definition-of-done for security requirements.

### Defensive techniques

- **OWASP Proactive Controls** — [owasp.org/www-project-proactive-controls](https://owasp.org/www-project-proactive-controls/) — ten defensive techniques developers should apply in every application: define security requirements, leverage security frameworks, secure database access, encode and escape data, validate all inputs, implement digital identity correctly, enforce access controls, protect data everywhere, implement security logging and monitoring, handle all errors and exceptions.

### Language- and framework-specific guidance

Generic security training does not stick as well as guidance tied to the developer's actual stack. Use the [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) as a reference by topic and language:

| Language / Area | Key cheat sheets and pitfalls |
|---|---|
| Python | [SQL Injection Prevention](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html), avoiding `pickle` deserialization, safe `subprocess` usage, SSRF prevention |
| Java / Spring | [Spring Security](https://cheatsheetseries.owasp.org/cheatsheets/Spring_Security_Cheat_Sheet.html), avoiding `ObjectInputStream`, XXE in XML parsers, expression language injection |
| JavaScript / Node.js | Prototype pollution, ReDoS, path traversal in file operations, [npm dependency confusion](https://cheatsheetseries.owasp.org/cheatsheets/npm_Security_Cheat_Sheet.html) |
| Go | SQL injection in raw queries, TLS configuration, goroutine leaks in error paths |
| Terraform / Helm | [Infrastructure as Code](https://cheatsheetseries.owasp.org/cheatsheets/Infrastructure_as_Code_Security_Cheat_Sheet.html), hardcoded secrets, overly permissive IAM, unsafe default values |
| Authentication | [Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html), [Session Management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html) |
| Cryptography | [Cryptographic Storage](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html), [TLS](https://cheatsheetseries.owasp.org/cheatsheets/TLS_Cipher_String_Cheat_Sheet.html) |

### Secure code review

How to read code adversarially — spotting anti-patterns, data flow from untrusted input to dangerous sinks, missing authorization checks, and insecure defaults. Code review is where security knowledge directly translates into prevented vulnerabilities.

A minimal secure code review checklist:
- [ ] All inputs validated server-side (type, length, allowlist where feasible)
- [ ] Parameterized queries used for all database access; no string concatenation
- [ ] Authorization checked on every state-changing operation, not just at login
- [ ] Secrets not hardcoded; no API keys in source files or logs
- [ ] Error responses sanitized; no stack traces, internal paths, or query text exposed
- [ ] Cryptographic functions use current algorithms and library defaults (not custom implementations)
- [ ] Dependencies match the expected version; no unexpected additions

## Integrating training into the developer lifecycle

Training is most effective when it meets developers where they already are, rather than pulling them out of their workflow.

### Onboarding

Every new developer should complete security onboarding before or alongside technical onboarding:

- OWASP Top 10 awareness module (60–90 minutes, interactive)
- Language-specific cheat sheet review for their primary stack
- Introduction to internal tools (secrets scanner, SAST, pre-commit hooks) and how to interpret findings
- Introduction to the security champion for their team

### Ongoing development

| Touchpoint | Delivery |
|---|---|
| IDE security plugin | Real-time feedback (Snyk, SonarLint, Semgrep) as code is typed |
| PR review | Automated comments linking findings to cheat sheet remediation guidance |
| Sprint planning | Security champion reviews relevant findings before estimation |
| Quarterly learning sprints | 2–4 hour focused lab on a current threat (e.g., LLM prompt injection, supply-chain attacks) |
| Incident retrospectives | Post-mortems that include secure-coding lessons from real vulnerabilities |

## Defining a secure coding standard

Every organization should maintain a written secure coding standard — a living document that captures language-specific rules, approved libraries, and banned patterns. Minimum contents:

1. **Approved dependency sources** — permitted registries, prohibited packages, lockfile requirements
2. **Authentication and session** — required auth library, forbidden patterns (rolling your own JWT validation, storing tokens in localStorage)
3. **Input and output handling** — validation libraries to use, encoding requirements per output context
4. **Database access** — ORM or query builder required, raw query rules
5. **Secrets management** — where secrets live (vault, environment variables), what is forbidden (committed plaintext, hardcoded strings)
6. **Cryptography** — approved algorithms and key sizes; forbidden (MD5, SHA1 for security purposes, DES, ECB mode)
7. **Error handling** — what to log, what to return in error responses
8. **Third-party code** — review requirements before adoption, license check, security advisory monitoring

Link the standard from pull request templates so it is visible at review time.

## What makes training stick

- **Hands-on, not slideware** — interactive labs and deliberately vulnerable apps beat passive video lectures. A developer who exploits a SQL injection in a lab will remember it; one who watches a slide about it will not.
- **Just-in-time** — surface a short, relevant lesson at the moment a developer hits a related finding in their IDE or PR review. Context and motivation are both highest at the point of discovery.
- **Role-relevant** — tailor content to the language, framework, and threat surface the developer works in.
- **Continuous** — short, frequent refreshers beat an annual compliance video. Aim for touchpoints at least quarterly.

## Training delivery patterns

| Pattern | When it works best |
|---|---|
| Self-paced labs (platform-provided) | Baseline training, onboarding, async organizations |
| Just-in-time IDE nudges | Language-specific, integrated into daily workflow |
| Live workshops | Threat modeling, code review, high-engagement topics |
| CTF / bug bash events | Team building, gamification, surfacing advanced interest |
| Champion-led team sessions | Team-specific context, local tooling and codebase examples |
| Incident-driven retrospective labs | High relevance — recreating a real vulnerability builds lasting memory |

## Reinforce in the AI era

With AI coding assistants generating a growing share of code, developers need to learn to:

- **Review AI-generated code** with the same scrutiny as hand-written code — AI assistants routinely produce SQL injection, path traversal, insecure deserialization, and other vulnerabilities.
- **Recognize hallucinated dependencies** — AI assistants sometimes suggest package names that do not exist, which attackers pre-register (a pattern called slopsquatting). Verify every suggested package.
- **Apply secure-coding judgment to AI output** — the developer is responsible for what they merge, regardless of who or what wrote it.
- **Use AI as a teaching moment** — when a scanner flags AI-generated code, treat it as a just-in-time training opportunity rather than just a fix-and-move-on task.

See [IDE and AI-Assisted Development Security](../../2-Process/2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md).

## Measuring training effectiveness

Completion rates are a compliance metric, not a security metric. Track:

| Metric | What it measures |
|---|---|
| Security defect escape rate (pre-production vs production) | Whether training translates to fewer runtime vulnerabilities |
| Security findings per developer per quarter (trend) | Injection rate improvement over time |
| Mean time to remediate findings (MTTR) | Developer fluency with fixing security issues |
| % of PRs with at least one security finding | Coverage and discovery health |
| Developer satisfaction score for security tooling | Friction — high friction correlates with workarounds |
| Time-to-first-security-finding after onboarding | Leading indicator of onboarding effectiveness |

## Maturity progression

| Level | Focus |
|---|---|
| Starting | OWASP Top 10 awareness; annual (or onboarding) completion; basic injection and XSS labs |
| Developing | Role-specific training tied to stack; just-in-time IDE integration; quarterly refreshers |
| Maturing | ASVS-aligned curriculum; escape rate tracked per team; training completion tied to sprint planning |
| Advanced | Developer-led threat modeling; champions deliver peer training; custom labs from internal incidents |

---

## Tools[^1]

### Open-source

- [OWASP Juice Shop](https://owasp.org/www-project-juice-shop/) — Modern, intentionally insecure web application covering the OWASP Top 10 and beyond. Ideal for workshops and self-study; includes a Capture the Flag mode. Best for broad web security awareness.
- [OWASP Security Knowledge Framework (SKF)](https://www.securityknowledgeframework.org/) — Provides security requirements, code examples, and labs mapped to ASVS. Supports integration into the development workflow. Best for teams wanting ASVS-aligned learning paths.
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/) — Deliberately insecure Java application with interactive lessons. Good for teams on JVM stacks; covers a wide set of Java-specific vulnerabilities.
- [OWASP crAPI](https://github.com/OWASP/crAPI) — Completely Ridiculous API, a vulnerable API for practising OWASP API Top 10 attacks. Ideal for teams building or testing APIs.

### Commercial

- [Hack The Box](https://www.hackthebox.com/) — Hands-on hacking labs and training for both offensive and defensive skills. Best for engineers with security interest who want to go beyond awareness into technical depth.
- [Secure Code Warrior](https://www.securecodewarrior.com/) — Gamified, language-specific secure-coding training integrated into the developer workflow; supports tournament-style team challenges. Best for enterprise-scale developer programs with manager dashboards.
- [SecureFlag](https://www.secureflag.com/) — Hands-on secure-coding training in real, runnable environments across 30+ languages and frameworks. Best for breadth of language support.
- [Snyk Learn](https://learn.snyk.io/) — Free and integrated secure coding lessons mapped to real CVEs and language-specific vulnerabilities. Best for just-in-time learning tied to actual Snyk findings.

---

### Links

[^1]: Listed in alphabetical order.
