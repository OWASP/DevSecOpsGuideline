# Security Chaos Engineering

Security controls are usually tested in the state they were designed for: the log pipeline is up, the secrets manager answers, the admission controller is running, and the network looks the way the diagram says. Real incidents rarely happen in that state. **Security chaos engineering** deliberately introduces failures and unexpected changes into a system to learn how its security controls behave when things go wrong, and whether anyone notices.

The practice applies chaos engineering, popularized by Netflix for availability, to security. Each experiment starts with a hypothesis such as "if the log shipper on a node stops, the SOC is alerted within 15 minutes", injects the failure in a controlled way, and compares what happened with what was expected. The results show where controls fail open, where detection has blind spots, and where the team's mental model of the system is wrong.

## How it differs from BAS and pentesting

- **Pentesting** looks for vulnerabilities an attacker could exploit, at a point in time. See [Pentest](2-7-3-Pentest.md).
- **[Breach and attack simulation](2-7-6-Breach-and-attack-simulation.md)** replays known attacker techniques to check that detection and prevention catch them.
- **Security chaos engineering** changes the conditions the controls depend on, such as an outage, a misconfiguration, a lost telemetry source, or an expired certificate, and checks that the system stays safe and that the failure is visible.

The three work together. BAS asks "do we detect this technique?", while a chaos experiment asks "do we still detect it when the agent that would see it is down?".

## Running an experiment

1. **Pick a security assumption.** Good candidates come from threat models, incident reviews, and architecture diagrams: "the WAF fails closed", "a privileged pod is always rejected", "an unexpected inbound rule is reverted within five minutes".
2. **Write the hypothesis and the expected signals.** State what should happen and how you will observe it: an alert, a blocked request, an automatic rollback, a ticket.
3. **Limit the blast radius.** Start in a test environment or with one instance, one namespace, or one account. Define stop conditions and a tested rollback before starting.
4. **Inject the failure.** Use a chaos tool or a scripted change, so the experiment is repeatable and can be stopped.
5. **Observe and compare.** Record what fired, what did not, and how long it took. A silent failure is the most valuable result.
6. **Fix and repeat.** Turn findings into backlog items for controls, detections, or runbooks, then run the experiment again to confirm the fix. Experiments that pass can be automated and scheduled.

## Example experiments

### Detection and telemetry

- Stop the log shipper or the runtime security agent (for example Falco) on one node, and check that missing telemetry raises an alert instead of a quiet gap.
- Drop or delay traffic between the log pipeline and the SIEM, and check how long the backlog takes to arrive and whether alerts on the delayed events still fire.
- Change a log format field that a detection rule depends on, and check whether the rule fails loudly or silently. See [Incident Response and Detection Engineering](2-7-10-Incident-Response-and-Detection-Engineering.md).

### Kubernetes and workloads

- Try to deploy a privileged pod, a pod running as root, or an image from an untrusted registry while the admission controller is degraded, and check whether the webhook fails closed. See [Kubernetes Runtime Policy Enforcement](2-7-7-Kubernetes-Runtime-Policy-Enforcement.md).
- Remove a NetworkPolicy from a namespace, and check that the drift is detected and reverted by GitOps or policy tooling.
- Make the secrets manager or the external secrets operator unavailable, and check that workloads keep running safely without falling back to hardcoded or default credentials. See [Secrets in Kubernetes and GitOps](../2-6-Deploy/2-6-2-Secrets-in-Kubernetes-and-GitOps.md).

### Cloud and network

- Open an unexpected port in a security group or firewall rule, and check that posture management or an automated remediation catches it, and how quickly.
- Create an access key for a service account outside the normal pipeline, and check that the change is detected.
- Make the identity provider or authorization service unavailable, and check that applications deny access rather than allowing it.

### Certificates and keys

- Let a certificate expire in a test environment, or rotate a signing key, and check that clients fail safely and that expiry monitoring alerted in time.

## Example: log shipper outage with Chaos Mesh

The hypothesis: "If the log shipper on one node is unavailable for ten minutes, the SIEM raises a missing telemetry alert within fifteen minutes."

```yaml
# Chaos Mesh: make one log shipper pod unavailable for 10 minutes
apiVersion: chaos-mesh.org/v1alpha1
kind: PodChaos
metadata:
  name: log-shipper-outage
  namespace: logging
spec:
  action: pod-failure
  mode: one
  duration: "10m"
  selector:
    namespaces:
      - logging
    labelSelectors:
      app.kubernetes.io/name: fluent-bit
```

While the experiment runs, generate a known suspicious event on the affected node, then check whether the missing telemetry alert fired, whether the suspicious event arrived once the shipper recovered, and whether the detection for it still triggered on the late data.

## Game days

Not every experiment needs a tool. A game day is a scheduled session where engineers and the security operations team run a scenario together, such as "the cloud audit log stops arriving" or "a CI runner is compromised", and walk through what the system and the people actually do. Game days test runbooks, escalation paths, and access to the right dashboards, which automated experiments cannot check. Agree up front whether the SOC is told about the exercise; an unannounced run tests detection and response more honestly, but needs sign-off from leadership.

## Running experiments safely

- Get agreement from the service owners and the security operations team on scope, timing, and stop conditions.
- Start in non-production, and move to production only for experiments that passed there and have a small, well-understood blast radius.
- Never disable a control in production without a compensating control and a time limit.
- Make every experiment stoppable, and test the rollback before the experiment.
- Mark experiment activity clearly in logs and tickets so it is not mistaken for a real incident afterwards, unless the goal is to test the response itself.

## Common pitfalls and anti-patterns

- **Breaking things without a hypothesis.** Random failure injection produces noise, not learning. Each experiment needs an expected outcome to compare against.
- **Only testing prevention.** Many of the most useful findings are about detection: the control failed and nobody noticed.
- **Starting in production.** Early experiments often expose large gaps. Find those in a test environment first.
- **No follow-up.** An experiment that finds a silent failure but produces no fix or ticket has only proven the gap.
- **Running experiments once.** Systems change, and a control that held last quarter can fail after the next migration. Automate the experiments that pass and run them on a schedule.

## Maturity progression

**Starter** - Run a game day for one scenario, such as a lost log source or an unavailable secrets manager, in a test environment. Record the gaps and fix the most important one.

**Intermediate** - Maintain a catalog of security hypotheses drawn from threat models and incidents. Run tool-based experiments in staging every quarter, including telemetry loss, admission control degradation, and cloud drift.

**Advanced** - Experiments that passed run automatically on a schedule, including carefully scoped ones in production. Results feed detection engineering and the risk register, and every major architecture change adds new hypotheses to the catalog.

## Metrics and KPIs

- **Hypotheses tested** - number of security assumptions tested per quarter, and the share that held.
- **Silent failures found** - experiments where a control failed and no alert fired.
- **Time to detect** - from failure injection to the first alert or automated response.
- **Fail-open controls** - number of controls found to allow access or traffic when degraded, and how many have been fixed.
- **Findings closed** - share of experiment findings fixed and confirmed by a repeat run.

---

## Tools[^1]

### Open-source

- [Chaos Mesh](https://chaos-mesh.org/) - CNCF chaos engineering platform for Kubernetes with pod, network, I/O, time, and kernel faults defined as custom resources.
- [Chaos Toolkit](https://chaostoolkit.org/) - Declarative experiment framework with extensions for Kubernetes, AWS, Azure, and Google Cloud; experiments are JSON or YAML files that fit well in CI.
- [krkn](https://github.com/krkn-chaos/krkn) - Chaos and resilience testing for Kubernetes and OpenShift clusters, including node, network, and zone outages.
- [LitmusChaos](https://litmuschaos.io/) - CNCF chaos engineering platform for Kubernetes with a large library of experiments and scheduling through workflows.

### Commercial

- [AWS Fault Injection Service](https://aws.amazon.com/fis/) - Managed fault injection for AWS resources, with stop conditions tied to CloudWatch alarms.
- [Azure Chaos Studio](https://azure.microsoft.com/products/chaos-studio/) - Managed fault injection for Azure resources and AKS.
- [Gremlin](https://www.gremlin.com/) - Reliability and chaos engineering platform with a library of infrastructure and network attacks and safety controls.
- [Steadybit](https://steadybit.com/) - Chaos engineering platform with guided experiments, an extension model, and safeguards for production use.

---

### Links

- [Security Chaos Engineering: Sustaining Resilience in Software and Systems (Kelly Shortridge and Aaron Rinehart, O'Reilly)](https://www.oreilly.com/library/view/security-chaos-engineering/9781098113810/)
- [Principles of Chaos Engineering](https://principlesofchaos.org/)

[^1]: Listed in alphabetical order.
