# AI Agent and MCP Security

Coding agents go beyond suggesting code: they read repositories and external content, run shell commands, edit many files, call APIs, and invoke tools through the Model Context Protocol (MCP) — usually with the developer's own privileges. [IDE and AI-assisted development](2-2-2-IDE-and-AI-assisted-development.md) introduces these risks; this page covers the controls to apply when agents and MCP servers are part of the engineering workflow. The guiding principle is **least agency**: give an agent only the autonomy, tools, and access its task requires, for only as long as it needs them.

## Threat model

An agent combines three things that are dangerous together: access to private data, exposure to untrusted content, and the ability to act or communicate externally. Any content the agent reads — an issue, a web page, a dependency README, a tool description — can carry instructions that the model may follow.

The [OWASP Top 10 for Agentic Applications (2026)](https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/) is a useful vocabulary. Its categories include Agent Goal Hijack (ASI01), Tool Misuse and Exploitation (ASI02), Identity and Privilege Abuse (ASI03), Agentic Supply Chain Vulnerabilities (ASI04), Unexpected Code Execution (ASI05), and Human-Agent Trust Exploitation (ASI09). Map your controls to these in threat modeling (see [Threat Modeling](../2-1-Design/2-1-1-Threat-modeling.md)); the broader governance view is in [AI Governance and Risk](../../3-Governance/3-4-AI-Governance-and-Risk.md).

## Agent identity and credentials

- Give agents their **own identity** (a service account, GitHub App, or bot user) rather than reusing a developer's personal credentials, so actions are attributable and revocable independently.
- Issue **scoped, short-lived tokens** per task (for example, via OIDC or a secrets manager) and never place long-lived or production credentials in the agent's environment, prompts, or config files. See [Secrets Management](2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md).
- Assume anything in the agent's process environment, shell history, or `.env` files can be read and sent out by an injected instruction.
- Keep agent identities out of administrative roles; separate read-only from write-capable identities.

## Tool permissions and least privilege

Start from deny and allow explicitly. Most coding agents offer permission rules and approval modes; configure them in version-controlled, reviewable project settings and use organization-managed policy where available.

```json
// Illustrative agent permission policy (syntax varies by product)
{
  "permissions": {
    "allow": ["Read(src/**)", "Bash(npm test)", "Bash(git diff *)"],
    "deny": ["Read(.env*)", "Read(~/.ssh/**)", "Bash(curl *)", "Bash(git push *)"]
  }
}
```

Treat the exact keys as product-specific and check the vendor's documentation. The pattern is what matters: allowlist read and test commands, deny secret locations and unrestricted network or push access, and require approval for everything else.

## Sandboxing and isolation

Permission prompts are not a security boundary against a manipulated agent; isolation is. Run agents where the worst case is contained:

- Use the agent's **OS-level sandbox** where it exists (several products now offer filesystem and network restrictions), and understand its scope — some sandboxes cover only shell commands, not file tools or MCP servers.
- Prefer a **dev container, disposable VM, or cloud environment** with no production credentials and no mounts of the home directory (see [Developer Workstation and Dev Container Security](2-2-4-Developer-Workstation-and-Dev-Container-Security.md)).
- **Restrict network egress** to an allowlist of required domains; this is the main control against data exfiltration after a successful injection. Hosted agents such as GitHub's Copilot cloud agent ship with a configurable firewall, with documented limits.
- Avoid "skip permissions" or full-access modes outside an isolated, throwaway environment.

## Prompt injection and tool poisoning

- Treat all external and user-controlled content as untrusted input to the agent: issues, pull request text, web pages, logs, dependency files, and MCP tool descriptions and responses.
- **Tool poisoning** — a malicious server can hide instructions in tool metadata, and a server can change its tool descriptions after you approved it. Re-review when tool definitions change, and prefer clients that surface or pin them.
- **Poisoned instruction files** — `AGENTS.md`, rules files, and similar configuration steer every session. Put them under CODEOWNERS, review them like code, and scan for hidden Unicode characters.
- Do not rely on the model to detect injections; assume it can be fooled and limit the damage through permissions, isolation, and egress control.

## MCP server vetting and supply chain

An MCP server is code (or a remote service) that runs with access you grant it. Local servers often execute as the developer, as the [MCP security best practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices) describe in its "Local MCP Server Compromise" section.

- Maintain an **approved server registry**; block ad hoc installation of unreviewed servers through managed client policy.
- Vet each server: source repository, maintainers, license, permissions requested, and what data it can reach. Prefer servers you host or that come from the system's own vendor.
- **Pin versions** (exact version or image digest) instead of `npx some-server@latest`, and verify before upgrading. Review the exact startup command a configuration will run.
- Prefer `stdio` transport for local servers or authenticated, least-scope remote servers; require OAuth with minimal scopes, and never pass client tokens through to downstream APIs (the specification forbids token passthrough).
- Run local servers sandboxed, with restricted filesystem and network access.
- Scan MCP server dependencies with SCA like any other software.

## Human-in-the-loop approvals

Keep a human decision at the points where harm is hard to undo: pushing code, merging, deploying, deleting data, sending messages, spending money, changing permissions, and any network access to a new destination.

- Show exact commands and tool arguments in the approval prompt, not a summary.
- Avoid approval fatigue: reduce prompts by safely allowlisting low-risk actions and sandboxing, rather than by approving everything.
- Never let an agent approve or merge its own pull requests; require independent human review (see [Secure Code Review](2-2-3-Secure-Code-Review.md)).

## Audit logging and monitoring

- Log every tool call, command, file write, and network request with the agent identity, the initiating user, the session, and the resulting diff.
- Send logs to a central system outside the agent's control, and retain them per policy; avoid logging secret values.
- Alert on anomalies: access to credential files, unexpected destinations, bulk reads, new MCP servers, or changes to instruction files and CI configuration.

## Policy-as-code for agent permissions

Express agent and MCP rules as versioned, testable policy instead of per-developer settings:

- Distribute organization-managed client settings that enforce allowed tools, sandbox mode, and server allowlists.
- Evaluate tool-call requests against policy in a gateway or proxy (for example, with Open Policy Agent or Cedar) to allow, deny, or require approval by identity, tool, and arguments.
- Validate committed agent configuration in CI: reject wildcard permissions, unpinned servers, and disabled sandboxes.

```rego
# Illustrative OPA rule: block unpinned MCP servers in committed config
package agent.mcp

deny[msg] {
  some name
  server := input.mcpServers[name]
  contains(server.args[_], "@latest")
  msg := sprintf("MCP server %v must pin an exact version", [name])
}
```

## Common pitfalls and anti-patterns

- **Running agents with the developer's full credentials** — compromised or misled agents inherit everything.
- **Blanket auto-approve on a laptop** — removes the checkpoint with no isolation to compensate.
- **Installing MCP servers from a blog post or `@latest`** — an unreviewed supply-chain dependency with code execution.
- **Trusting tool descriptions** — metadata is model input and can contain instructions.
- **Treating the sandbox as total** — sandboxes often cover only part of the agent's capabilities; verify what is in scope.
- **No logs** — without an audit trail, an injection incident cannot be investigated.

## Maturity progression

| Level | Practice |
|---|---|
| Starter | Approval prompts left on; no production credentials in agent environments; list of approved agents and MCP servers; AI usage policy published |
| Intermediate | Committed, reviewed permission settings; agents run in dev containers or sandboxes with egress allowlists; pinned MCP servers; agent instruction files under CODEOWNERS |
| Advanced | Dedicated agent identities with short-lived scoped tokens; organization-managed policy-as-code and gateway enforcement; centralized audit logging with anomaly alerts; regular red-team exercises on prompt injection and tool poisoning |

## Metrics and KPIs

- Percentage of agent sessions running in a sandbox or isolated environment.
- Number of approved versus unapproved MCP servers detected.
- Percentage of MCP servers pinned to an exact version or digest.
- Count of agent actions requiring human approval versus auto-approved, and approval-denial rate.
- Number of agent sessions with access to long-lived credentials (target zero).
- Time to detect and revoke a misbehaving agent identity.

---

## Tools[^1]

### Open-source

- [Cedar](https://www.cedarpolicy.com/) — Policy language and engine for fine-grained authorization decisions, usable to authorize tool calls.
- [Docker MCP Gateway](https://github.com/docker/mcp-gateway) — Runs and mediates MCP servers in containers with centralized configuration.
- [Open Policy Agent](https://www.openpolicyagent.org/) — General-purpose policy engine for expressing agent and MCP rules as code.
- [promptfoo](https://github.com/promptfoo/promptfoo) — Testing and red-teaming framework for LLM applications and agents, including prompt injection scenarios.
- [Sandbox Runtime (Anthropic)](https://github.com/anthropic-experimental/sandbox-runtime) — Experimental OS-level filesystem and network sandbox for arbitrary processes, including MCP servers.

### Commercial

- [Claude Code sandboxing and permissions](https://code.claude.com/docs/en/sandboxing) — OS-enforced sandbox for shell commands with filesystem and network controls, plus permission rules.
- [Codex agent approvals and security](https://developers.openai.com/codex/agent-approvals-security) — Sandbox modes and approval policies for the Codex agent, with admin-enforced requirements.
- [Cursor agent sandboxing](https://cursor.com/blog/agent-sandboxing) — Sandboxed terminal execution with network and filesystem controls.
- [GitHub Copilot cloud agent firewall](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-firewall) — Configurable network allowlist for the hosted coding agent.

---

### Links

[^1]: Listed in alphabetical order.

## Further reading

- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP Top 10 for LLM Applications](https://genai.owasp.org/llm-top-10/)
- [Model Context Protocol — Security best practices](https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices)
- [IDE and AI-assisted development](2-2-2-IDE-and-AI-assisted-development.md)
- [AI Governance and Risk](../../3-Governance/3-4-AI-Governance-and-Risk.md)
