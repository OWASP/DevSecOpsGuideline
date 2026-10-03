# Release

The release stage is the final checkpoint before software leaves the build pipeline and becomes a candidate for deployment. It is where all the earlier security work is consolidated into a verifiable, trustworthy package and where the final go/no-go decision is made. A disciplined release process ensures that only artifacts meeting your security bar — built from trusted source, scanned, signed, and documented — can move toward production.

## Security activities at release

- **Final security gate** — confirm there are no unresolved critical/high findings (or that exceptions are documented and approved). See [Security Gates](../2-3-Build/2-3-5-Security-Gates.md).
- **Attach supply-chain metadata** — bind the [SBOM](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md) and build [provenance](../2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md) to the release artifact.
- **Sign the artifact** — produce a cryptographic signature so downstream consumers and the deploy stage can verify integrity and origin.
- **Release approval** — capture sign-off (automated policy and/or human approval) and tie it to change management for auditability.
- **Security-relevant release notes** — document fixed vulnerabilities, CVE references, and changed security-affecting configurations so downstream consumers and operators have the information they need.

## Immutable, traceable artifacts

### Immutability

Once released, an artifact must never change. Any fix produces a new versioned artifact. Without this guarantee, a "tested" artifact can be silently substituted for a malicious one, and the test results become meaningless.

Enforce immutability technically:
- Enable **tag immutability** in your container registry (AWS ECR, GitHub Packages, Artifactory) so a published tag cannot be overwritten.
- Use **content-addressable references** (image digest `sha256:...`) in deployment manifests, not mutable tags like `latest` or `v1.2`.
- Protect release tags in source control: see [Repository Hardening](../2-2-Develop/2-2-1-Pre-commit/2-2-1-4-Repository-Hardening.md).

### Trusted registry

Publish artifacts to a controlled registry with:
- Access controls: only CI pipelines (via OIDC, not long-lived keys) can push; humans read-only.
- Retention policies: retain all released versions; automatically clean up pre-release candidates.
- Vulnerability scanning at rest: re-scan stored images as new CVEs are disclosed (many registries offer this natively).
- Signing: every pushed artifact is signed at publish time.

### Traceability

Every release should be traceable back to its exact source commit, build pipeline run, and the security scans that passed. SLSA signed provenance makes this linkage cryptographically verifiable:

```bash
# Verify a container image's provenance with cosign (Sigstore)
cosign verify-attestation \
  --type slsaprovenance \
  --certificate-identity-regexp "https://github.com/myorg/myrepo/.github/workflows/release.yml" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry/myimage:v1.2.3
```

The attestation proves: who built it, when, from which commit, using which workflow — without any additional trust in the registry.

## Promotion between environments

Mature pipelines build an artifact **once** and promote the same artifact through environments (test → staging → production) rather than rebuilding per environment:

- The artifact that passed security scans in test is *exactly* the artifact deployed to production — no re-build, no re-introduction of variance, no "it worked on staging" surprises.
- Before each promotion, re-verify the artifact's signature and provenance against the registry. An artifact that cannot be verified is not promoted.
- Use **GitOps** to make promotion declarative and auditable: a promotion is a pull request (image digest bump in the environment manifest), not a manual action or a shell script with credentials.

Example promotion gate with cosign:
```bash
# In the production promotion workflow
IMAGE_DIGEST=$(crane digest myregistry/myimage:v1.2.3)
cosign verify \
  --certificate-identity "...release.yml@refs/tags/v1.2.3" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  myregistry/myimage@$IMAGE_DIGEST || exit 1
```

## Release approval and change management

Different release categories warrant different approval models:

| Release category | Approval model |
|---|---|
| Patch / bug fix (low risk) | Automated policy check (OPA/Conftest) against artifact metadata; no human gate |
| Minor feature release | Automated gate + team lead approval in PR; auto-notifies change management |
| Major release or regulated system | Formal change request, named CAB approver, rollback plan documented in ServiceNow/Jira |
| Emergency hotfix | Expedited single-approver process; post-review required within 24 hours |

Automated policy checks via OPA or Conftest can evaluate artifact metadata (SBOM attached, signature present, no unresolved criticals, provenance verified) and produce a machine-readable attestation that human reviewers use as evidence — reducing cognitive load and audit effort.

## Common pitfalls and anti-patterns

- **Rebuilding per environment** — if a new build is created for production, all test results from the staging build are meaningless. Build once, promote everywhere.
- **Mutable tags in production** — using `latest` or a branch-name tag means deployments can inadvertently roll forward or back without an explicit decision.
- **Release notes with no security content** — downstream teams need to know which CVEs were fixed and which security behaviors changed to assess their own exposure.
- **Signing as a one-time event without verification at deploy** — signing is only valuable if the signature is actually verified before the artifact runs. Many teams sign but never verify.
- **Change management as a bureaucratic checkbox** — if the change management process adds weeks of delay without reducing risk, teams work around it. Automate low-risk approvals so the process has teeth where it matters.

## Maturity progression

**Starter** — Protect release tags in source control. Publish artifacts to a private registry. Include SBOM in release packages. Document final gate criteria.

**Intermediate** — Enforce tag immutability. Sign all release artifacts with cosign (keyless, OIDC). Automated OPA gate checks for low-risk releases. SBOM attached as registry attestation. Release notes include CVEs fixed.

**Advanced** — Full SLSA Level 3 provenance. Signature verification at every promotion stage. Automated policy approval for low-risk releases; human gate only for high-risk. Re-scan stored artifacts as new CVEs are published. Continuous SLA tracking for vulnerability remediation between releases.

## Metrics and KPIs

- **Percentage of releases with signed, attested provenance** — target 100%.
- **Mean time from critical CVE disclosure to release containing the fix** — measures responsiveness; define SLAs by severity.
- **Release rollback rate** — security-related rollbacks indicate insufficient pre-release gates.
- **Unsigned or unverified deployments** — any deployment of an unsigned artifact is an incident; should be zero.
- **Time in change management** — high average time indicates the approval process is a bottleneck; automate low-risk cases.

---

## Tools

| Category | Examples |
|---|---|
| Artifact registries | JFrog Artifactory, Sonatype Nexus, GitHub Packages, AWS ECR, Google Artifact Registry, Harbor (open source) |
| Container signing and verification | Sigstore/cosign (keyless, OIDC-based), Notary v2 (Docker Content Trust) |
| Provenance and SLSA | SLSA framework, GitHub Actions OIDC + sigstore, in-toto, Tekton Chains |
| Policy-based release approval | OPA/Conftest, Kyverno, Open Policy Agent admission webhook |
| Change management integration | ServiceNow, Jira Service Management, PagerDuty Change Events |
| GitOps promotion | Argo CD (ApplicationSets + image-updater), Flux, Spinnaker |

---

## Further reading

- [SLSA — provenance and verification](https://slsa.dev/)
- [NIST SSDF — PS (Protect the Software) practices](https://csrc.nist.gov/Projects/ssdf)
- [CNCF Software Supply Chain Best Practices](https://github.com/cncf/tag-security)
- [Sigstore — keyless signing](https://www.sigstore.dev/)
- [Harbor — open source container registry](https://goharbor.io/)
- [OpenSSF — Securing the Software Supply Chain](https://openssf.org/)
