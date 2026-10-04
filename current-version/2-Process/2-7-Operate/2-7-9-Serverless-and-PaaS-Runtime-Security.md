# Serverless and PaaS Runtime Security

Serverless functions and managed container platforms remove the operating system, patching, and host hardening from your to-do list, but they do not remove risk. They move it. The attack surface shifts to **identity and permissions, event inputs, third-party dependencies, secrets, and configuration** — the parts the provider explicitly leaves to the customer under the shared responsibility model. Because functions are short-lived, numerous, and often wired to many event sources, a single over-permissioned function can become the easiest path into a cloud account.

This section covers how to secure workloads on function platforms (AWS Lambda, Azure Functions, Google Cloud Functions) and managed container platforms (Google Cloud Run, Azure Container Apps, AWS App Runner and Fargate-style services). Platform-level controls such as clusters and nodes are covered in [Cloud-Native Security](2-7-1-Cloud-Native-Security.md).

## Shared responsibility on serverless and PaaS

| Layer | Function platform (FaaS) | Managed container platform (PaaS) |
|---|---|---|
| Physical, hypervisor, host OS | Provider | Provider |
| Runtime and language patches | Provider (managed runtimes) / You (custom runtimes, container images) | You (base image and runtime in your container) |
| Application code and dependencies | You | You |
| Identity, permissions, and network access | You | You |
| Secrets and configuration | You | You |
| Event sources and triggers | You | You |
| Logging, detection, and response | You (provider supplies the audit logs) | You |

Two consequences follow: managed runtimes reach end of life and must be upgraded by you, and the "no servers to patch" claim never applies to your own libraries or container base images.

## Least-privilege identity per function

The most common serverless failure is a shared or wildcard execution role. Give **every function its own identity** scoped to the exact actions and resources it needs:

- **AWS Lambda** — one execution role per function; avoid managed policies such as `AdministratorAccess` and wildcard resources; use IAM Access Analyzer to generate a policy from observed CloudTrail activity.
- **Azure Functions** — use a managed identity (system-assigned, or user-assigned where several resources must share one) with narrowly scoped RBAC assigned at resource level rather than subscription level.
- **Google Cloud Run and Cloud Functions** — run each service as a dedicated user-managed service account instead of the default compute service account; grant only specific roles on specific resources.

```yaml
# Example: AWS SAM function with a narrowly scoped, per-function policy
Resources:
  OrdersReader:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      Runtime: python3.13
      Policies:
        - DynamoDBReadPolicy:
            TableName: !Ref OrdersTable   # one table, read-only, no wildcards
```

Treat **invocation permissions** (who may trigger the function) as a separate control from the execution role (what the function may do). Both need review.

## Event-injection and input validation

Functions are triggered by many more event types than a classic web app — HTTP, queues, object-storage notifications, message topics, stream records, scheduled events, and database changes. Every one of them carries attacker-influenced data, and teams often validate only the HTTP path.

- **Validate every event source**, not just API Gateway or HTTP triggers. A file name in an object-storage event or a message body from a queue can contain shell metacharacters, SQL, or path traversal sequences.
- Validate against a schema (JSON Schema or the framework's event validators) and reject unexpected fields.
- Never pass event fields to a shell, `eval`, or string-built queries; use parameterized queries and library APIs.
- Apply [DAST](../2-4-Test/2-4-2-Dynamic-Application-Security-Testing.md) and fuzzing to the non-HTTP triggers as well, using crafted test events.
- Apply request limits, concurrency caps, and timeouts to bound abuse and denial-of-wallet attacks.

## Dependencies, layers, and container images

Functions typically bundle many third-party packages, often via shared layers or copied-in base images that nobody owns.

- Run [SCA](../2-3-Build/2-3-2-Software-Composition-Analysis/2-3-2-1-Software-Composition-Analysis.md) on every function and generate an [SBOM](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) per deployable artifact, so you can answer "which functions contain this library?" within minutes.
- Treat **shared layers and extensions as a supply-chain risk**: they execute with the function's permissions. Pin versions, restrict who can publish them, and scan them like any other dependency.
- For container-based platforms, scan and harden images ([Container Scanning](../2-3-Build/2-3-3-Container-Security/2-3-3-1-Container-Scanning.md), [Container Hardening](../2-3-Build/2-3-3-Container-Security/2-3-3-2-Container-Hardening.md)) and deploy only signed images; Cloud Run and similar platforms can enforce this at deploy time with policy.
- Track runtime end-of-life dates and upgrade deprecated language runtimes on a schedule.

## Secrets and short-lived credentials

- Prefer **platform identity over stored credentials**: IAM roles, managed identities, and workload identity federation remove static keys altogether.
- Where a secret is unavoidable, keep it in a managed secret store (AWS Secrets Manager, Azure Key Vault, Google Secret Manager) and fetch it at runtime with caching and a short TTL. Plain environment variables are visible to anyone with configuration read access and often appear in logs and crash dumps.
- Rotate secrets automatically and scope each secret to the one function that needs it.
- Run [secret scanning](../2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md) on function code and deployment templates.

## Observability and runtime protection without agents

You usually cannot install a host agent on a function platform, so detection relies on provider and in-function telemetry:

- **Control-plane and audit logs** — CloudTrail, Azure Activity Log, and Cloud Audit Logs show who changed a function, role, or trigger. Alert on new function URLs, role changes, and layer updates.
- **Data-plane logs** — emit structured, correlated application logs and traces from the function (for example with the Powertools libraries on Lambda or OpenTelemetry) and forward them to the central platform described in [Logging and Monitoring](2-7-2-Logging-and-Monitoring.md).
- **Behavioral signals** — unusual invocation volume, new outbound destinations, spikes in errors or duration, and access to resources the function has never touched.
- **Network controls** — place functions in a private network only when they need private resources; use egress filtering where available so a compromised function cannot call arbitrary hosts.
- **Instrumentation options** — some commercial tools offer in-function runtime protection through layers or sidecars; evaluate the performance and cold-start cost before adopting. On container platforms with sidecar support, runtime sensors can be added to the service definition.
- **Posture checks** — continuously scan accounts for public function URLs, wildcard roles, unencrypted environment variables, and deprecated runtimes.

## Common pitfalls and anti-patterns

- **One shared execution role for all functions** — a compromise of any one function inherits the union of all permissions.
- **Wildcard permissions "just to make it work"** — `Action: *` or `Resource: *` left in place after development.
- **Validating only HTTP input** — queue, storage, and stream triggers treated as trusted internal data.
- **Secrets in environment variables or code** — visible in console, logs, and templates.
- **Unowned layers and base images** — shared components that nobody scans or updates.
- **Public function endpoints by default** — unauthenticated function URLs or ingress left open.
- **Assuming the provider secures the runtime** — forgetting that dependencies, custom images, and end-of-life runtimes are the customer's responsibility.
- **No logging beyond defaults** — no audit trail for configuration changes and no application-level security events.

## Maturity progression

**Starter** — Inventory all functions and managed-container services. Remove wildcard and shared roles on the highest-risk functions. Move secrets out of environment variables into a secret manager. Enable control-plane audit logging.

**Intermediate** — One least-privilege identity per function, defined in IaC and checked by [IaC scanning](../2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md) in CI. SCA and SBOM on every deployable. Input validation on all trigger types. Structured logging and alerts on configuration changes and anomalous invocations.

**Advanced** — Permissions generated from observed behavior and reviewed continuously. Signed, policy-enforced deployments. Layers and base images centrally owned and versioned. Runtime anomaly detection tied to automated containment (for example, revoking a function's role or throttling it to zero concurrency). Serverless scenarios included in [breach and attack simulation](2-7-6-Breach-and-attack-simulation.md).

## Metrics and KPIs

- **Functions with a dedicated execution identity** — percentage of functions not sharing a role; target 100%.
- **Functions with wildcard permissions** — count of functions whose policy allows `*` actions or resources; should trend to zero.
- **Static secrets in function configuration** — number found by scanning; should be zero.
- **Functions on deprecated runtimes** — count and age of runtimes past provider end of support.
- **SBOM coverage** — percentage of deployed functions and services with a current SBOM.
- **Non-HTTP trigger test coverage** — percentage of event sources covered by input-validation tests.
- **Mean time to contain** a compromised function in an exercise.

---

## Tools[^1]

### Open-source

- [Cartography](https://github.com/cartography-cncf/cartography) — Maps cloud assets and relationships (AWS, GCP, Azure, and others) into a Neo4j graph, useful for answering which functions can reach which data stores.
- [Checkov](https://github.com/bridgecrewio/checkov) — Static analysis of IaC templates (SAM, CloudFormation, Terraform, and others) for over-permissive roles and insecure function and service settings.
- [Cloud Custodian](https://github.com/cloud-custodian/cloud-custodian) — Rules engine that detects and automatically remediates cloud misconfigurations, including public function URLs and non-compliant function settings.
- [Falco](https://github.com/falcosecurity/falco) — CNCF-graduated runtime threat detection for Linux hosts and Kubernetes; applicable to self-managed serverless platforms such as Knative, not to provider-managed function runtimes.
- [Powertools for AWS Lambda](https://github.com/aws-powertools/powertools-lambda) — Developer toolkit (Python, TypeScript, Java, .NET) providing structured logging, tracing, metrics, and event parsing and validation utilities for Lambda.
- [Prowler](https://github.com/prowler-cloud/prowler) — Open-source cloud security posture assessment for AWS, Azure, GCP, and Kubernetes, with checks covering serverless services.
- [Trivy](https://github.com/aquasecurity/trivy) — Scans function code dependencies, container images, and IaC for vulnerabilities, misconfigurations, and secrets.

### Commercial

- [Datadog Serverless Monitoring](https://www.datadoghq.com/product/serverless-monitoring/) — Tracing, logging, and metrics for functions and managed container services, with optional application security features.
- [Microsoft Defender for Cloud](https://learn.microsoft.com/azure/defender-for-cloud/) — Posture management and workload protection across Azure, AWS, and GCP, including Azure Functions and Container Apps.
- [Orca Security](https://orca.security/) — Agentless cloud security platform covering serverless and container workloads alongside broader cloud posture.
- [Prisma Cloud](https://www.paloaltonetworks.com/prisma/cloud) — Cloud-native application protection platform with serverless function scanning and runtime defense options.
- [Sysdig Secure](https://sysdig.com/products/secure/) — Cloud and container runtime security built on Falco, with coverage for serverless and managed container services.
- [Wiz](https://www.wiz.io/) — Agentless cloud security platform with graph-based risk analysis across functions, containers, and identities.

---

### Links

- [AWS Lambda security](https://docs.aws.amazon.com/lambda/latest/dg/lambda-security.html)
- [Azure Functions security](https://learn.microsoft.com/azure/azure-functions/security-concepts)
- [Google Cloud Run security overview](https://cloud.google.com/run/docs/securing/security)
- [OWASP Serverless Top 10](https://owasp.org/www-project-serverless-top-10/)

[^1]: Listed in alphabetical order.
