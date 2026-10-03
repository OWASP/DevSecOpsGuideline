# Container Scanning

Containers package an application together with its operating-system libraries and dependencies. That convenience also means a single image can carry hundreds of inherited vulnerabilities from its base layers and OS packages. **Container scanning** inspects images for known vulnerabilities, misconfigurations, and embedded secrets — across the build, the registry, and at deployment.

## The container vulnerability lifecycle

Understanding when and how vulnerabilities enter images is essential for an effective scanning strategy:

```
1. Base image published (debian:12, ubuntu:22.04, python:3.11-slim)
        │
        ▼
2. Your CI pulls the base image → vulnerability snapshot at pull time
        │
        ▼
3. Build: ADD application code, install dependencies (pip, npm, apt)
        │
        ▼
4. Image pushed to registry — clean at this point
        │
        ▼
5. New CVE disclosed against a library in the base image (days, weeks, months later)
        │
        ▼
6. Registry continuous scanning detects the new CVE in stored image
        │
        ▼
7. Alert → team must rebuild (base image bump) and redeploy
```

The critical insight: **a build-time scan is a point-in-time snapshot**. An image that passes today may fail tomorrow when a new CVE is disclosed against a library that was already present. This is why registry-level continuous scanning is not optional — it is the mechanism that catches post-build exposure.

## What container scanning checks

- **OS package vulnerabilities** — CVEs in the base image and installed system packages (glibc, openssl, zlib, etc.).
- **Application dependency vulnerabilities** — language libraries bundled into the image (overlaps with [SCA](../2-3-2-Software-Composition-Analysis/2-3-2-1-Software-Composition-Analysis.md), but scoped to what is inside the image layers).
- **Misconfigurations** — running as root, exposed ports, insecure defaults in the Dockerfile.
- **Embedded secrets** — credentials accidentally baked into image layers; note that a secret added in one layer and deleted in the next is still present in the image history and fully recoverable with `docker history`.
- **Malware / unexpected content** — files that should not be present, suspicious binaries, or unexpected network listeners.
- **License compliance** — OS packages often carry different licenses than application code.

## Where to scan

Scan at multiple points so nothing slips through:

- **Build time** — scan the image as part of CI immediately after the build step; gate on severity before pushing to any registry.
- **Registry** — continuously rescan stored images, since *new* CVEs are disclosed against images that were clean when built. Most enterprise registries (Harbor, ECR, Artifact Registry) support built-in continuous scanning.
- **Admission / deploy time** — block non-compliant or unsigned images from reaching the cluster (see [Deploy](../../2-6-Deploy/2-6-1-Deploy.md)). This is the last line of defense.

```yaml
# Example: Trivy scan in GitHub Actions at build time
- name: Build Docker image
  run: docker build -t myapp:${{ github.sha }} .

- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: myapp:${{ github.sha }}
    format: sarif
    output: trivy-results.sarif
    severity: HIGH,CRITICAL
    exit-code: '1'

- name: Upload Trivy SARIF
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

## Generating SBOMs from container images

Container scanning and SBOM generation are complementary. Generate an SBOM from the built image to capture exactly what packages are present at runtime — not what the source code imports, but what the image actually contains:

```bash
# Generate a CycloneDX SBOM from a container image using Syft
syft myapp:latest -o cyclonedx-json > sbom.json

# Attach the SBOM as a signed attestation to the registry (requires cosign)
cosign attest --predicate sbom.json \
  --type cyclonedx \
  myregistry/myapp@$(crane digest myregistry/myapp:latest)

# Later: verify and retrieve the SBOM
cosign verify-attestation --type cyclonedx myregistry/myapp:latest | \
  jq '.payload | @base64d | fromjson | .predicate'
```

This SBOM can then be ingested by Dependency-Track for continuous CVE monitoring against the image's exact component inventory. See [SBOM](../2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) for the full SBOM workflow.

## Multi-architecture image scanning

Multi-arch images (`linux/amd64`, `linux/arm64`) can have different vulnerabilities per platform because they pull different OS packages from the base image. Ensure scanning covers all target architectures:

```bash
# Scan specific platform explicitly
trivy image --platform linux/arm64 myapp:latest

# Scan all platforms in a manifest list
for platform in linux/amd64 linux/arm64; do
  trivy image --platform $platform myapp:latest
done
```

CI pipelines that build multi-arch images must scan each variant — a vulnerability in the `arm64` image does not appear in an `amd64` scan.

## Reducing inherited risk: distroless and minimal images

The most effective way to cut container vulnerabilities is to start from a minimal base. The numbers are stark:

| Base image | Approximate CVE count | Shell available |
|---|---|---|
| `ubuntu:22.04` | 30–80 CVEs (varies) | Yes |
| `debian:12-slim` | 15–40 CVEs (varies) | Yes |
| `python:3.11-slim` | 20–50 CVEs (varies) | Yes (via debian-slim) |
| `gcr.io/distroless/python3` | 0–5 CVEs | No |
| `gcr.io/distroless/static` | 0–2 CVEs | No |
| `scratch` | 0 | No |

**Distroless images** (Google's `gcr.io/distroless/*`) ship no shell, no package manager, and no unnecessary OS tools. An attacker who achieves code execution in a distroless container has almost no utilities to work with — no `curl`, no `wget`, no `bash`, no `apt`. This dramatically reduces the blast radius of any container escape.

**Multi-stage builds** achieve the same result for compiled languages:

```dockerfile
# Stage 1: build (full toolchain)
FROM golang:1.22 AS builder
WORKDIR /app
COPY . .
RUN go build -o /bin/myapp ./cmd/myapp

# Stage 2: runtime (minimal — no Go toolchain, no compilers)
FROM gcr.io/distroless/static-debian12:nonroot AS runtime
COPY --from=builder /bin/myapp /bin/myapp
USER nonroot:nonroot
ENTRYPOINT ["/bin/myapp"]
```

The builder stage, with its compilers and development dependencies, never ships. The runtime image is a clean, minimal artifact.

## Pinning base images to digests

Tags are mutable — `python:3.11-slim` today may not be the same image as `python:3.11-slim` tomorrow:

```dockerfile
# BAD: tag is mutable
FROM python:3.11-slim

# GOOD: pinned to immutable digest
FROM python:3.11-slim@sha256:abc123def456...
```

Combine digest pinning with a weekly automated rebuild (Dependabot, Renovate, or a scheduled CI job) that bumps the digest and rescans. This ensures you absorb upstream security patches without introducing unvetted changes.

## Common pitfalls and anti-patterns

- **Scanning only in CI, not in the registry** — a vulnerability disclosed six months after an image was built will never be caught without continuous registry scanning.
- **Scanning the wrong layer** — running SCA on source code and separately scanning the image can produce discrepancies. The image scan is authoritative for what actually ships.
- **Using `:latest` tags for base images** — always pin to digests in production Dockerfiles; mutable tags break reproducibility and scanning consistency.
- **Secrets committed in an earlier layer** — adding a secret in one layer and removing it in the next does not remove it from the image history. Use `--secret` at build time or pass secrets at runtime via the orchestrator.
- **Alert fatigue from base-image noise** — a base image upgrade can introduce dozens of new OS-level CVEs. Filter by severity and prioritize those with public exploits or runtime reachability context.
- **Not scanning multi-arch variants** — vulnerabilities in the `arm64` variant do not appear in an `amd64` scan.

## Maturity progression

**Starter** — Run Trivy or Grype on every image in CI. Block on critical severity. Do not push unscanned images to the registry.

**Intermediate** — Enable continuous registry scanning (Harbor, ECR native scanning, or Trivy Operator in Kubernetes). Gate deployments with an admission controller that rejects images with unresolved criticals. Migrate base images to minimal/distroless equivalents. Pin base images to digests.

**Advanced** — Generate SBOMs for every image with Syft; attach as signed attestations; ingest into Dependency-Track for continuous monitoring. Automate weekly base image rebuilds via Dependabot/Renovate. Use reachability analysis to differentiate exploitable from theoretical OS CVEs. Scan all multi-arch variants. Track base image age and vulnerable-image-days as KPIs.

## Metrics and KPIs

| Metric | Target |
|---|---|
| Images with unresolved critical CVEs in production | 0 |
| Mean age of base images before rebuild | < 30 days |
| Registry scan freshness | < 24 hours per image |
| % of images using minimal/distroless base | > 80% |
| Images pinned to digest (not tag) | 100% in production |
| Images with attached, signed SBOM in registry | 100% |

---

## Tools[^1]

### Open-source

- [Clair](https://github.com/quay/clair) — Static analysis of vulnerabilities in container images; powers scanning in Quay and other registries; best for self-hosted registry integration rather than CI pipelines.
- [Dockle](https://github.com/goodwithtech/dockle) — Container image linter focused on Dockerfile best practices and CIS benchmark alignment; complements vulnerability scanners rather than replacing them.
- [Grype](https://github.com/anchore/grype) — Fast vulnerability scanner for container images and filesystems; pairs naturally with Syft for SBOM-driven scanning. Best for CI pipelines needing a lightweight, scriptable CLI.
- [Syft](https://github.com/anchore/syft) — SBOM generator for container images and filesystems; produces SPDX and CycloneDX; the standard pairing for Grype.
- [Trivy](https://github.com/aquasecurity/trivy) — Comprehensive scanner for images, filesystems, IaC, and SBOMs; single binary, easy CI integration, broad vulnerability database. Best all-in-one option for most teams.

### Commercial

- [Docker Scout](https://www.docker.com/products/docker-scout/) — Integrated image analysis and base-image remediation guidance built into Docker Hub and Docker Desktop. Best for teams heavily in the Docker ecosystem.
- [Snyk Container](https://snyk.io/product/container-vulnerability-management/) — Container vulnerability scanning with base-image recommendations and automatic Dockerfile fix PRs. Strong developer experience.
- [Wiz](https://www.wiz.io/) — Cloud and container vulnerability management as part of a CNAPP; strong for correlating image findings with actual cloud exposure and runtime context.

---

### Links

[^1]: Listed in alphabetical order.
