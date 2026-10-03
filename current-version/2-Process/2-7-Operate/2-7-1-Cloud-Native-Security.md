# Cloud-Native Security (CNAPP)

Once software is deployed, security shifts from preventing flaws to **detecting and containing** threats in a live, dynamic environment. Cloud-native applications — containers, Kubernetes, serverless, and managed cloud services — change constantly and span many layers, which traditional perimeter tools cannot cover. The industry has converged on the **Cloud-Native Application Protection Platform (CNAPP)**: a unified approach that brings posture management and runtime protection together across code, cloud, and workloads.

## What CNAPP brings together

CNAPP consolidates capabilities that used to be separate products:

| Capability | What it does | Why it matters |
|---|---|---|
| **CSPM** (Cloud Security Posture Management) | Continuously checks cloud configuration for misconfigurations and compliance drift | Catches S3 bucket ACL changes, security group drift, IAM privilege accumulation |
| **KSPM** (Kubernetes Security Posture Management) | Posture management for Kubernetes clusters, namespaces, and workloads | Detects missing Pod Security Standards, exposed dashboards, overprivileged service accounts |
| **CWPP** (Cloud Workload Protection Platform) | Protects running workloads — containers, VMs, functions — with threat detection | Detects cryptomining, reverse shells, lateral movement inside running containers |
| **CIEM** (Cloud Infrastructure Entitlement Management) | Analyzes and right-sizes cloud identities and permissions | Surfaces IAM roles with `*:*` permissions, stale credentials, cross-account privilege paths |
| **CDR** (Cloud Detection and Response) | Correlates signals into attack storylines and drives response | Connects a failed authN attempt to a subsequent privilege escalation to a data exfil |

By correlating signals across these layers — and back to code — CNAPP prioritizes the risks that are genuinely exploitable rather than treating every finding equally.

## Runtime protection essentials

### Threat detection with eBPF

Modern runtime protection uses **eBPF** (extended Berkeley Packet Filter) to attach observers to the Linux kernel without loadable kernel modules, providing:
- Full syscall visibility at near-zero overhead.
- Process lineage: which parent spawned which child, with what arguments.
- Network connection tracking: which process opened which socket to which destination.
- File access: reads/writes to sensitive paths (`/etc/shadow`, credential files, PKI directories).

Falco uses eBPF to apply declarative rules against this stream:
```yaml
# Falco rule: detect shell spawned inside a container
- rule: Terminal Shell in Container
  desc: A shell was used as the entrypoint or is run interactively in a container
  condition: >
    spawned_process and container
    and proc.name in (shell_binaries)
    and proc.tty != 0
  output: >
    Shell opened in container (user=%user.name container=%container.name
    image=%container.image.repository:%container.image.tag
    proc=%proc.name cmdline=%proc.cmdline)
  priority: WARNING
```

### Network policy and zero trust

Default Kubernetes networking allows any pod to talk to any pod on any port. Apply default-deny network policies immediately:

```yaml
# Default deny all ingress and egress — apply per namespace
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

Then add explicit allow rules for required communication paths only. Use a service mesh (Istio, Linkerd) for mTLS between services and fine-grained L7 policy.

### Drift detection

Alert when the running state diverges from the declared, reviewed GitOps state:
- A Kubernetes admission controller prevented a bad deploy — but a manual `kubectl exec` that modifies a running container is drift.
- IaC defined a security group — but an operator added an inbound rule in the console. CSPM catches this and alerts.
- Detect file integrity changes inside containers (writes to binary directories, new executables) as indicators of compromise.

### Workload identity

Static secrets embedded in workloads are a persistent attack surface. Use platform-native workload identity instead:
- **AWS IRSA** (IAM Roles for Service Accounts) — Kubernetes pods assume AWS IAM roles via short-lived OIDC tokens; no AWS access keys stored anywhere.
- **GCP Workload Identity Federation** — analogous for GCP services.
- **SPIFFE/SPIRE** — standards-based workload identity for cross-cloud and non-cloud workloads; issues short-lived X.509 SVIDs.

## Closing the loop

Runtime findings should not stay in operations — feed them back into [Vulnerability Management](2-7-4-Vulnerability-Management.md) and [ASPM](../../3-Governance/3-3-Reporting/3-3-3-ASPM.md) so production context (what is actually exposed, reachable, and under active attack) informs how earlier-stage findings are prioritized. This runtime-to-code feedback loop is the essence of "shift everywhere":

- A CVE in a container image is critical if that image is running in a production cluster and the vulnerable component is reachable from the internet.
- The same CVE in an image never pulled is informational.
- Runtime detection of exploitation confirms that a theoretical finding is a real incident.

## Common pitfalls and anti-patterns

- **Alert fatigue from untuned CSPM** — a fresh CSPM deployment against a brownfield cloud environment produces thousands of findings. Start with critical and high severity; establish a remediation SLA before enabling more rules.
- **Agent deployed but findings never acted on** — runtime security is only valuable if findings trigger a response. Connect Falco or CWPP alerts to your SIEM/SOAR incident workflow from day one.
- **Network policies without testing** — a misconfigured network policy can break service communication silently. Test policies in staging with realistic traffic before enforcing in production.
- **CNAPP replacing application security** — CNAPP covers infrastructure and workload posture; it does not replace SAST, SCA, or code review. They are complementary layers.
- **Overly broad CIEM remediation** — removing cloud permissions without understanding dependencies can break production services. Use CIEM's "last used" data to identify safe removals and test in staging.

## Maturity progression

**Starter** — Deploy CSPM (Prowler or cloud-native Security Hub/Security Center). Enable Falco in your Kubernetes cluster with default rules. Apply default-deny network policies per namespace. Migrate from static credentials to IRSA/Workload Identity.

**Intermediate** — Tune CSPM to remove false positives; achieve < 20 open high/critical findings. Falco alerts route to SIEM. Drift detection enabled. CIEM analysis run quarterly to right-size IAM. eBPF-based runtime agent deployed to all nodes.

**Advanced** — Full CNAPP platform correlating CSPM + CWPP + CIEM + CDR signals. Runtime context feeds ASPM for application-level risk prioritization. Automated remediation for common CSPM findings (Lambda closes public S3 ACLs). SPIFFE/SPIRE for workload identity across multi-cloud. Active red team exercises validate detection coverage.

## Metrics and KPIs

- **CSPM critical/high open finding count** — track per cloud account; define remediation SLAs.
- **Mean time to detect (MTTD)** — time from anomalous runtime event to alert generation.
- **Mean time to respond (MTTR)** — time from alert to containment action.
- **Percentage of workloads using workload identity (no static credentials)** — target 100%.
- **Network policy coverage** — percentage of namespaces with explicit network policies applied.
- **IAM permissions reduction** — percentage decrease in unused permissions removed by CIEM-driven remediation.

---

## Tools[^1]

### Open-source

- [Falco](https://falco.org/) — CNCF runtime security engine that detects anomalous behavior using eBPF/kernel events; extensive rule library and active community; integrates with SIEM, Slack, and SOAR platforms.
- [Kubescape](https://github.com/kubescape/kubescape) — Kubernetes posture management and compliance scanning against NSA/CISA, CIS, and MITRE ATT&CK frameworks; developer-friendly CLI and IDE integrations.
- [Trivy Operator](https://github.com/aquasecurity/trivy-operator) — Continuous vulnerability and misconfiguration scanning inside clusters; generates VulnerabilityReport and ConfigAuditReport CRDs that integrate with dashboards.
- [Wazuh](https://wazuh.com/) — Open-source security platform with threat detection, file integrity monitoring, and SIEM-like capabilities; useful for VM workloads alongside container-focused tools.
- [Cilium](https://cilium.io/) — eBPF-based networking and security for Kubernetes; provides network policy enforcement at L3/L4/L7, hubble observability, and transparent mTLS encryption.

### Commercial

- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud) — Full CNAPP covering CSPM, CWPP, CIEM, and code security in a single platform; strong compliance reporting for regulated industries.
- [Sysdig Secure](https://sysdig.com/products/secure/) — Runtime security and CNAPP built on Falco; adds policy management, incident response, and CSPM to open-source Falco.
- [Wiz](https://www.wiz.io/) — Agentless CNAPP for cloud posture and risk prioritization; graph-based attack path analysis that connects misconfiguration to blast radius without requiring agents.

---

### Links

[^1]: Listed in alphabetical order.
