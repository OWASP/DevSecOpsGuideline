# AI/LLM Application Security Testing and Red Teaming

Applications built on large language models (LLMs) fail in ways that SAST, DAST, and SCA were not designed to find. The model's behavior is probabilistic, its inputs include untrusted natural language (and documents, web pages, and tool outputs it reads on the user's behalf), and its outputs may drive real actions through tools and APIs. **AI/LLM application security testing** treats the whole system — model, prompts, retrieval pipeline, tools, and the permissions behind them — as the attack surface, and repeatedly probes it the way an adversary would. **AI red teaming** adds human creativity on top of automated evals to find the failures a fixed test suite will not.

This page covers testing. For policy, risk classification, and oversight see [AI Governance and Risk](../../3-Governance/3-4-AI-Governance-and-Risk.md); for securing the AI coding tools your developers use, see [IDE and AI-assisted development](../2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md).

## What to test: the OWASP Top 10 for LLM Applications

Use the [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/) as the test-planning checklist (the 2025 edition is referenced here; check the OWASP GenAI Security Project for newer editions). The categories that most often need dedicated test cases:

| Risk | Example test |
|---|---|
| **LLM01 Prompt Injection** | Direct overrides ("ignore previous instructions"), and *indirect* injection hidden in retrieved documents, emails, web pages, or tool results |
| **LLM02 Sensitive Information Disclosure** | Coax the model to reveal PII, secrets, or other tenants' data from context, memory, or training data |
| **LLM05 Improper Output Handling** | Check whether model output reaches a browser, shell, SQL engine, or template unescaped (XSS, SSRF, command injection via the LLM) |
| **LLM06 Excessive Agency** | Can an injected instruction make an agent call a tool, send data, or modify resources beyond what the user is entitled to? |
| **LLM07 System Prompt Leakage** | Extract the system prompt, and verify nothing in it is a secret or the only access control |
| **LLM08 Vector and Embedding Weaknesses** | Poison or cross-tenant-query the vector store; test retrieval authorization |
| **LLM10 Unbounded Consumption** | Token floods, recursive agent loops, and expensive tool calls that cause denial of service or runaway cost |

The [OWASP GenAI Red Teaming Guide](https://genai.owasp.org/resource/genai-red-teaming-guide/) structures an engagement across four areas: model evaluation, implementation testing, infrastructure assessment, and runtime behavior analysis. [MITRE ATLAS](https://atlas.mitre.org/) provides an ATT&CK-style catalogue of adversary techniques against AI systems that you can map findings to.

## Testing agents, tools, and MCP

Agentic systems turn prompt injection from a content problem into an authorization problem. Test the blast radius, not just the model:

- **Tool permission review** — enumerate every tool, API scope, and credential the agent holds. Each should be least-privilege, scoped to the *end user's* identity where possible, and require human approval for destructive or irreversible actions.
- **Indirect injection via tool output** — plant adversarial instructions in a file, ticket, web page, or MCP tool response and verify the agent does not follow them to call other tools or exfiltrate data.
- **Data-exfiltration channels** — check whether an injected agent can leak context through rendered markdown images/links, outbound HTTP tools, email, or logs.
- **MCP server trust** — treat third-party [Model Context Protocol](https://modelcontextprotocol.io/) servers like third-party code: pin versions, review tool descriptions for hidden instructions ("tool poisoning"), and test for cross-server tool shadowing. See [Supply Chain Security](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) for provenance practices.
- **Sandboxing** — confirm code-execution and browsing tools run isolated, without ambient credentials or network access to internal services.

## Automated probing in the pipeline

A minimal [promptfoo](https://www.promptfoo.dev/) red-team configuration targeting an HTTP endpoint:

```yaml
# promptfooconfig.yaml
targets:
  - id: https
    config:
      url: https://staging.example.com/api/chat
      method: POST
      body: { message: "{{prompt}}" }
      transformResponse: json.reply
redteam:
  purpose: "Customer-support assistant; must never reveal other customers' data or call refund tools without approval"
  plugins:
    - owasp:llm          # preset mapped to the OWASP LLM Top 10
  strategies:
    - jailbreak
    - prompt-injection
```

Run it from CI against a staging deployment and gate on the result:

```yaml
# .github/workflows/llm-redteam.yml (excerpt)
- name: LLM red-team evals
  env:
    # Provider key used to generate attacks and grade results; store in CI secrets
    OPENAI_API_KEY: ${{ secrets.REDTEAM_PROVIDER_KEY }}
  run: |
    npx promptfoo@latest redteam run -c promptfooconfig.yaml -o redteam-results.json
    # exit code is non-zero when failures exceed the configured threshold
```

Check the current tool documentation for exact flags, as these CLIs change quickly. Generic scanners such as [garak](https://github.com/NVIDIA/garak) work the same way: *probes* generate adversarial interactions and *detectors* judge whether the output shows a failure.

## Making evals a reliable gate

- **Define pass/fail by risk, not by average** — a single successful leak of customer data is a failure even if 99% of attempts are refused. Set per-category thresholds, with zero tolerance for the most severe.
- **Run on every change that can alter behavior** — prompt edits, model or version swaps, new tools, retrieval-source changes, and guardrail changes, not just code commits.
- **Pin and record** — store model version, system prompt hash, tool manifest, and seed in the results so regressions are reproducible. Expect non-determinism: run multiple trials and track failure rates.
- **Keep a regression corpus** — every confirmed bypass from red teaming or production becomes a permanent test case.
- **Test the guardrails separately** — measure the false-negative and false-positive rates of input/output filters, and do not rely on them as the only control.
- **Protect the test data** — attack corpora and results can contain harmful content and real data; handle them under the same classification rules as production.

## Common pitfalls and anti-patterns

- **Treating the system prompt as a security boundary** — instructions in a prompt can be overridden; enforce access control and limits in code and in tool permissions.
- **Testing the model, not the application** — a safe base model wired to an over-privileged tool is still exploitable. Test end-to-end, including retrieval and tools.
- **A one-time red team before launch** — models, prompts, and data sources drift. Without continuous evals the assurance expires quickly.
- **Using the model under test as its own judge** — LLM graders have blind spots and can be manipulated; use a separate grader, spot-check with humans, and keep deterministic checks where possible.
- **Chasing jailbreak scores while ignoring agency** — content-policy bypasses matter less than whether an injected instruction can move data or change state.
- **Testing only in English, only direct input** — multilingual, encoded, multi-turn, and indirect (document-borne) attacks are common bypasses.

## Maturity progression

**Starter** — Inventory LLM-enabled features and the tools/data each can reach. Run a generic scanner (garak or promptfoo) manually against staging, and review the OWASP LLM Top 10 against your architecture. Remove unnecessary tool permissions.

**Intermediate** — Automated red-team evals in CI against staging for prompt, model, and tool changes, with category thresholds that fail the build. Indirect-injection and output-handling test cases for every RAG and tool integration. Human approval gates on high-impact tool actions. Findings tracked like other vulnerabilities.

**Advanced** — Continuous evals plus periodic human-led red teaming following the OWASP GenAI Red Teaming Guide. Production telemetry (blocked injections, anomalous tool calls) feeds the regression corpus. Per-user, scoped credentials for agents, MCP server allow-listing and review, and findings mapped to MITRE ATLAS. Results reported to AI governance.

## Metrics and KPIs

- **Attack success rate by category** — percentage of adversarial attempts that succeed, tracked per OWASP LLM risk and per release.
- **Eval coverage** — percentage of LLM-enabled features, tools, and RAG sources with automated red-team cases.
- **Time to remediate confirmed bypasses** — from discovery to fixed and added to the regression corpus.
- **Agent permission footprint** — number of tools/scopes per agent, and percentage of high-impact actions behind human approval.
- **Regression rate** — previously fixed bypasses that reappear after a model, prompt, or tool change; target zero.

---

## Tools[^1]

### Open-source

- [DeepTeam](https://github.com/confident-ai/deepteam) — LLM red-teaming framework with vulnerability and attack modules aligned to the OWASP LLM Top 10; from the Confident AI team behind DeepEval.
- [garak](https://github.com/NVIDIA/garak) — NVIDIA's LLM vulnerability scanner; large library of probes and detectors for jailbreaks, prompt injection, leakage, and more.
- [Giskard](https://github.com/Giskard-AI/giskard-oss) — Open-source testing library for LLM agents with scenario-based checks and a vulnerability scan (v3 is a rewrite; v2 is no longer actively maintained).
- [promptfoo](https://github.com/promptfoo/promptfoo) — MIT-licensed CLI and library for evals and red teaming, with OWASP-mapped plugins and CI integration; OpenAI announced plans to acquire the company in March 2026 and both state it remains open source.
- [PyRIT](https://github.com/microsoft/PyRIT) — Microsoft's Python Risk Identification Tool; framework for orchestrating multi-turn and multimodal attacks against generative AI systems.

### Commercial

- [HiddenLayer](https://hiddenlayer.com/) — AI security platform covering model scanning, runtime detection, and automated red teaming.
- [Lakera](https://www.lakera.ai/) — Runtime guardrails and red-teaming for LLM applications and agents (now part of Check Point).
- [Mindgard](https://mindgard.ai/) — Automated AI red teaming and continuous security testing.
- [Protect AI (Palo Alto Networks)](https://protectai.com/) — AI/ML security including model scanning and LLM red teaming (Recon); acquired by Palo Alto Networks.

---

### Links

- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- [OWASP GenAI Red Teaming Guide](https://genai.owasp.org/resource/genai-red-teaming-guide/)
- [MITRE ATLAS](https://atlas.mitre.org/)

[^1]: Listed in alphabetical order.
