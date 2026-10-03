# Container Hardening

Scanning tells you what is *wrong* with an image; **hardening** is how you build images that are right by construction — small, minimal-privilege, and resistant to compromise. A hardened container limits both the likelihood of a vulnerability being exploitable and the blast radius if one is exploited. Defense-in-depth applies at every layer: image content, runtime configuration, and cluster policy.

## Build a minimal image

Every package, binary, and layer you include is a potential attack surface. The goal is to ship only what the application needs to run:

- **Use minimal or distroless base images** — every package you omit is a vulnerability you cannot inherit. Google's [distroless images](https://github.com/GoogleContainerTools/distroless) contain only a language runtime and application code — no shell, no package manager, no debugging tools. An attacker who achieves code execution has nowhere to go.
- **Multi-stage builds** — compile in a full build stage and copy only the final artifact into a clean minimal runtime stage:

  ```dockerfile
  # Build stage
  FROM golang:1.22 AS builder
  WORKDIR /app
  COPY . .
  RUN CGO_ENABLED=0 go build -o myapp ./cmd/server

  # Runtime stage — no build tools, no shell
  FROM gcr.io/distroless/static-debian12
  COPY --from=builder /app/myapp /myapp
  ENTRYPOINT ["/myapp"]
  ```

- **Pin base images to digests** — mutable tags (`:latest`, `:22.04`) can change without warning. Pin to an immutable digest and automate periodic base image rebuilds:

  ```dockerfile
  FROM ubuntu@sha256:abc1234... AS base
  ```

- **No secrets in layers** — every layer is permanently part of the image history. Use `--secret` mounts for build-time secrets and runtime environment injection for all credentials.

## Run with least privilege

A container that runs as root and has broad Linux capabilities is one kernel exploit away from a full host compromise:

- **Non-root user** — always set a non-root `USER` in the Dockerfile. For distroless images, use the nonroot variant:

  ```dockerfile
  USER nonroot:nonroot
  ```

- **Read-only root filesystem** — mount the container filesystem read-only; declare explicit writable volumes only where needed:

  ```yaml
  # Kubernetes pod spec
  securityContext:
    readOnlyRootFilesystem: true
  volumeMounts:
    - name: tmp
      mountPath: /tmp
  volumes:
    - name: tmp
      emptyDir: {}
  ```

- **Drop Linux capabilities** — start from zero and add back only what is required. Most application containers need no capabilities at all:

  ```yaml
  securityContext:
    capabilities:
      drop: ["ALL"]
      add: []   # add only if explicitly required, e.g. NET_BIND_SERVICE
    allowPrivilegeEscalation: false
  ```

- **No privileged containers** — avoid `--privileged` and host namespace sharing (`hostPID`, `hostNetwork`, `hostIPC`). These break container isolation entirely.
- **Resource limits** — set CPU and memory limits to contain denial-of-service conditions and runaway workloads. An unconstrained container can starve co-located services.

## Verify against benchmarks

Measure image and runtime configuration against established security baselines rather than relying on internal convention:

- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker) — covers the Docker daemon, image build practices, and container runtime configuration.
- [CIS Kubernetes Benchmark](https://www.cisecurity.org/benchmark/kubernetes) — covers the Kubernetes control plane, worker nodes, and etcd configuration.
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) — defines three profiles (Privileged, Baseline, Restricted); enforce the `Restricted` profile for all production workloads via namespace labels and admission controllers.
- Run **kube-bench** and **Docker Bench for Security** as part of CI for infrastructure validation.

## Tie into the supply chain

Hardened images should also be **signed and traceable**. Sign images with cosign/Sigstore and attach provenance (SLSA) and SBOMs as attestations so that only verified, hardened images are admitted to production — see [Artifact Signing and Provenance](../2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md) and [Container Scanning](2-3-3-1-Container-Scanning.md).

## Common pitfalls and anti-patterns

- **Hardening the Dockerfile but leaving a debug sidecar running in production** — sidecars with shells and tools negate the work done in the main container.
- **`USER` set to a non-root UID but without a matching group** — some applications rely on group membership; verify runtime behavior after adding the USER directive.
- **Assuming distroless means invulnerable** — distroless dramatically reduces the attack surface but the language runtime and your application code still carry their own vulnerabilities. Scanning remains necessary.
- **Resource limits set too tight** — containers that hit memory limits are OOM-killed; set limits based on real profiling, not guesses.
- **Build tools left in final image** — compilers, package managers, and test frameworks significantly increase image size and attack surface. Enforce multi-stage builds in code review.

## Maturity progression

**Starter** — Enforce non-root `USER` in all Dockerfiles. Add hadolint to CI to lint Dockerfiles. Remove obviously unnecessary packages from base images.

**Intermediate** — Migrate to distroless or minimal base images. Enforce multi-stage builds. Add `readOnlyRootFilesystem: true` and drop all capabilities in Kubernetes manifests. Run kube-bench in CI for infrastructure pipelines.

**Advanced** — Pin all base images to digests; automate weekly rebuilds. Sign images with Sigstore keyless signing and verify at admission with Kyverno or the Sigstore policy controller. Enforce `Restricted` pod security standards cluster-wide. Use Chainguard Images for critical base images; track CVE count and mean severity of base images as operational KPIs.

## Metrics and KPIs

| Metric | Target |
|---|---|
| % of containers running as non-root | 100% |
| % of containers with read-only root filesystem | > 90% |
| % of containers with all capabilities dropped | > 90% |
| % of images using minimal/distroless base | > 80% |
| kube-bench score (CIS benchmark pass rate) | > 95% |

---

## Tools[^1]

### Open-source

- [Docker Bench for Security](https://github.com/docker/docker-bench-security) - Checks Docker hosts and containers against CIS benchmark recommendations; useful as a configuration audit step.
- [Dockle](https://github.com/goodwithtech/dockle) - Dockerfile and image linter for security best practices; catches common misconfigurations before the image is built.
- [hadolint](https://github.com/hadolint/hadolint) - Dockerfile linter enforcing best practices including multi-stage build patterns, pinned digests, and non-root USER; integrates with most CI systems and IDEs.
- [kube-bench](https://github.com/aquasecurity/kube-bench) - Checks Kubernetes cluster configuration against the CIS Kubernetes Benchmark; runs as a job in the cluster or in CI for infrastructure pipelines.

### Commercial

- [Chainguard Images](https://www.chainguard.dev/) - Continuously rebuilt, SLSA-signed minimal container base images with near-zero CVEs; eliminates base-image vulnerability debt by design.
- [Sysdig Secure](https://sysdig.com/products/secure/) - Container hardening, drift detection, and runtime security for Kubernetes; detects when a running container deviates from its hardened image.

---

### Links

[^1]: Listed in alphabetical order.
