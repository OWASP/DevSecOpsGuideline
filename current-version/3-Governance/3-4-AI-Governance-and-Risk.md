# AI Governance and Risk

AI has become embedded across the software lifecycle — assistants generate code, models power product features, and agents act autonomously in pipelines. This creates new risks that traditional AppSec does not fully cover, and new governance obligations. AI governance establishes the policies, controls, and accountability for using AI **safely and responsibly** in both how you build software and what you ship.

## Two faces of AI risk

### 1. AI in the SDLC

The use of AI coding assistants (GitHub Copilot, Cursor, Amazon Q, Claude) and AI agents in pipelines introduces risks at the development layer:

- **Insecure generated code** — LLMs produce code with OWASP Top 10 flaws (injection, broken auth, insecure deserialization) at measurable rates. Studies show AI-generated code fails security review more often than human-written code on average when developers accept suggestions without scrutiny.
- **Hallucinated dependencies (slopsquatting)** — LLMs invent package names that do not exist, creating supply-chain risk if a malicious actor registers those names.
- **Data leakage to third-party models** — developers submitting proprietary code, PII, or credentials to external AI services may violate data protection obligations.
- **Prompt injection via code context** — malicious content in a codebase (e.g., a file deliberately crafted to manipulate an AI agent's actions) can redirect AI behavior in unexpected ways.

See [IDE and AI-Assisted Development Security](../2-Process/2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md) for controls.

### 2. AI in the product

Securing LLM- and ML-powered features you build and operate:

- **Prompt injection** — malicious user input or content retrieved from external sources manipulates the model's behavior, causing it to bypass safety guardrails or take unauthorized actions.
- **Insecure output handling** — LLM output fed into downstream systems (code execution, SQL, shell commands) without sanitization becomes an injection vector.
- **Training-data poisoning** — adversarially crafted data introduced into training sets can cause models to behave incorrectly in specific, hard-to-detect ways.
- **Sensitive-information disclosure** — models can memorize and regurgitate training data, including PII or proprietary content.
- **Excessive agency** — AI agents granted broad permissions can cause significant harm when manipulated or malfunctioning. An agent with access to production databases and email should raise the same alarm as a human with the same access.
- **Model theft / inversion** — adversaries can extract model behavior or training data through repeated querying.

## Key risk frameworks

- **[OWASP Top 10 for LLM Applications](https://genai.owasp.org/)** — the canonical risks for LLM-based systems: prompt injection, insecure output handling, training-data poisoning, model denial of service, sensitive-information disclosure, excessive agency, and more. Map every LLM-powered feature against this list at design time.
- **[OWASP Machine Learning Security Top 10](https://owasp.org/www-project-machine-learning-security-top-10/)** — risks specific to ML systems: input manipulation (evasion), data poisoning, model inversion, membership inference, and model theft.
- **[NIST AI Risk Management Framework (AI RMF)](https://www.nist.gov/itl/ai-risk-management-framework)** — a structured approach to governing AI risk across four functions: Govern, Map, Measure, Manage. Aligns AI risk management with organizational risk appetite.
- **[ISO/IEC 42001](https://www.iso.org/standard/81230.html)** — AI management system standard, analogous to ISO 27001 for information security. Provides a framework for responsible AI development and deployment.
- **[EU AI Act](https://artificialintelligenceact.eu/)** — risk-based regulation classifying AI systems from minimal to unacceptable risk, with mandatory requirements (transparency, conformity assessment, human oversight) for high-risk systems.

## Securing the ML pipeline (MLSecOps)

Extend DevSecOps discipline to the model lifecycle — models and datasets are supply-chain artifacts and must be treated with the same rigor as code:

- **Data and model provenance** — track where training data and pre-trained models come from. Record the source, version, and license. Use a model registry with immutable versioned artifacts, analogous to a container registry.
- **AI-BOM** — extend the [SBOM](../2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) concept to inventory models, datasets, fine-tuning data, and their dependencies. CycloneDX supports AI/ML bill of materials extensions.
- **Scan model artifacts** — serialized model files (pickle, safetensors, ONNX) can carry malicious code that executes on deserialization. Scan all externally sourced model files before loading. Prefer safetensors format over pickle; avoid `torch.load` with untrusted sources.
- **Protect the inference path** — validate and sanitize all inputs before they reach the model. Rate-limit model endpoints. Log inputs and outputs for abuse monitoring and forensics.
- **Guardrails** — apply prompt-injection defenses (input filtering, output validation, instruction hierarchy), output filtering (content policy enforcement, PII redaction), and least-privilege for any agent that can take actions.
- **Adversarial testing** — red-team LLM-powered features specifically for prompt injection, jailbreaks, and misuse before launch and after model updates. Use tools like Garak for automated probing.

## Governing AI use

### AI usage policy

Every organization using AI tools in the SDLC needs a policy that covers:

- **Which tools are approved** — maintain an approved list and a process for evaluating new tools. Unapproved tools used for work data are shadow IT.
- **What data may be shared** — define clearly which data classifications may be sent to external AI models. Assume that data sent to a SaaS AI model may be retained and used for training unless explicitly contractually excluded.
- **Where enterprise or self-hosted options are required** — for source code, PII, and confidential business data, require enterprise-tier agreements with data isolation guarantees, or self-hosted/on-premises models.
- **How AI-generated code must be reviewed** — require that AI-generated code receives the same security review as human-written code. Establish that acceptance of AI suggestions is the accepting developer's responsibility.

### Human accountability

AI assists, but humans remain accountable for what is merged and shipped:

- No AI-generated code is exempt from code review, security scanning, or testing.
- Require explicit sign-off for AI-generated security-critical code (authentication, authorization, cryptography).
- Document where AI is used in products and decisions — for transparency, for regulatory compliance, and to support post-incident investigation.

### Limiting agency

Constrain autonomous agents to the minimum permissions and actions required:

| Control | Implementation |
|---|---|
| Least privilege | Scoped API keys; read-only where possible |
| Action allowlisting | Agent may only call defined tool functions |
| Human-in-the-loop | Require approval for irreversible actions |
| Audit trail | Log all agent decisions and tool calls |
| Kill switch | Ability to pause or revoke agent credentials immediately |

### Transparency and oversight

- Disclose to users when they are interacting with an AI system where legally required (EU AI Act, FTC guidance).
- Monitor model behavior in production for drift, misuse, and unexpected outputs. Anomalies in output patterns are early warning signs of prompt injection attacks or model degradation.
- Review AI-generated content policies and guardrails regularly as adversarial techniques evolve.

## Maturity progression

**Starter** — an AI usage policy that defines approved tools and data-sharing rules. SAST and SCA run on AI-generated code as on any other. Developers informed about AI-specific risks.

**Intermediate** — enterprise AI tool agreements in place with data isolation. AI-BOM adopted for all internally-built AI features. LLM-powered features assessed against OWASP LLM Top 10 at design. Guardrails implemented. Adversarial testing before launch.

**Advanced** — ML pipeline secured end-to-end with model provenance, artifact signing, and scanning. AI-BOM integrated into software supply chain and ASPM. Continuous monitoring of model behavior in production. Automated prompt-injection testing in CI for LLM features. Compliance with EU AI Act requirements for applicable risk categories.

## Common pitfalls

- **Trusting AI-generated code without review** — AI tools produce plausible-looking code that contains real vulnerabilities. The developer's responsibility for security does not diminish because a tool wrote the code.
- **No approved tool list** — without one, developers use whatever is convenient, often sending proprietary data to services with no data protection agreement.
- **Excessive agent permissions** — granting an AI agent admin credentials "because it's easier" creates a high-blast-radius target. Any agent that can delete data or send email is a significant risk if manipulated.
- **Treating LLM output as trusted** — LLM outputs that flow into downstream systems (databases, shell commands, APIs) without sanitization are injection vulnerabilities.
- **No data residency consideration for AI** — sending EU customer data to a US-based AI API may violate GDPR data transfer requirements.

## Metrics

| Metric | What it tells you |
|---|---|
| % of AI-generated code that passes security review on first submission | Developer ability to produce secure AI-assisted code |
| Number of unapproved AI tools in use (shadow AI) | Governance gap; indicates policy is not being followed |
| LLM-powered features assessed against OWASP LLM Top 10 (%) | Security coverage of AI product surface |
| Prompt injection findings in adversarial testing | Robustness of AI feature defenses |
| AI-BOM coverage (% of AI features with documented model/data inventory) | Supply-chain visibility for AI components |

---

## Tools[^1]

### Open-source

- [Garak](https://github.com/NVIDIA/garak) — LLM vulnerability scanner. Probes LLM-powered applications for prompt injection, jailbreaks, data leakage, and more using hundreds of built-in attack probes. Use in CI for LLM-powered features.
- [ModelScan](https://github.com/protectai/modelscan) — scans ML model files (pickle, HDF5, Keras, PyTorch, TensorFlow SavedModel) for unsafe code that executes on deserialization. Run on all externally sourced model artifacts.
- [NeMo Guardrails](https://github.com/NVIDIA/NeMo-Guardrails) — toolkit for adding programmable guardrails to LLM applications: topic restrictions, output filtering, and dialog flow control. Supports multiple LLM backends.
- [PyRIT](https://github.com/Azure/PyRIT) — Python Risk Identification Toolkit for generative AI (by Microsoft). Automates red-teaming of LLM applications at scale.

### Commercial

- [HiddenLayer](https://hiddenlayer.com/) — security platform for AI/ML models: model scanning, adversarial attack detection at inference time, and model behavior monitoring.
- [Protect AI](https://protectai.com/) — security and governance for the AI/ML lifecycle. Covers model scanning (via ModelScan), supply chain security, and LLM guardrails.

---

### Links

[^1]: Listed in alphabetical order.
