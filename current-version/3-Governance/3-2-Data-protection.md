# Data Protection

Ultimately, most security exists to protect **data** — customer information, credentials, intellectual property, and regulated records. Data protection spans the controls and practices that keep data confidential, intact, and available throughout its lifecycle, and the privacy obligations that govern personal data. In a DevSecOps program, data protection cuts across every stage, from design through operation.

## Know your data: classification

You cannot protect data appropriately without knowing what you have and how sensitive it is. Classification is the foundation of proportionate protection:

- **Public** — no harm if disclosed (marketing content, documentation). Minimal controls.
- **Internal** — intended for employees and partners. Basic access control and logging.
- **Confidential** — business-sensitive data (financials, strategy, IP). Encryption, restricted access, audit trails.
- **Regulated / PII / PHI** — personal or legally-protected data (GDPR, HIPAA, PCI DSS). Strictest controls, data residency obligations, retention limits, and deletion rights.

Steps to operationalize classification:

1. **Inventory** — catalog all data stores (databases, object storage, data lakes, SaaS) and label them by classification. Automated data discovery tools accelerate this at scale.
2. **Tag at the source** — embed classification metadata in data catalog entries, resource tags, and infrastructure-as-code so controls can be applied programmatically.
3. **Apply controls proportionate to classification** — the most sensitive data gets the strongest encryption, most restricted access, and most complete audit trail.

## Core protective controls

### Encryption

- **Encryption in transit** — enforce TLS 1.2+ everywhere, including service-to-service traffic inside the cluster. Use mutual TLS (mTLS) for service mesh environments (Istio, Linkerd). Reject or redirect plaintext connections.
- **Encryption at rest** — encrypt databases, object storage (S3/GCS/Azure Blob), backups, and persistent volumes. Use platform-managed encryption as a baseline; for highest-sensitivity data, add application-layer or client-side encryption so the cloud provider cannot decrypt data at rest.
- **End-to-end encryption** — for data that must remain private even from your own infrastructure (e.g. health or financial records), consider E2E encryption where keys remain entirely with the data owner.

### Key management

- Manage keys in a dedicated KMS/HSM (AWS KMS, Azure Key Vault, GCP Cloud KMS, HashiCorp Vault) with automatic rotation, access control, and audit logging.
- Never hardcode keys or secrets in source code (see [Secrets Management](../2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md)).
- Separate keys by environment (dev/staging/prod); a compromised dev key must not decrypt production data.
- Enforce key expiry and rotation policies. For regulated data, document the key lifecycle.

### Access control

- Apply least-privilege access to all data stores: users and services receive the minimum permissions required for their function.
- Use strong authentication (MFA for human access to sensitive data; short-lived, scoped credentials for service access via OIDC/Workload Identity).
- Log all access to sensitive data — who accessed what, when, from where — and retain logs for the period required by your compliance obligations.
- Review data access permissions regularly; access rights granted for a project often outlast the project.

### Data Loss Prevention (DLP)

- Deploy DLP controls at egress points (email, cloud storage, SaaS integrations, developer endpoints) to detect and block unauthorized exfiltration.
- Define sensitive-data patterns for your context: PCI card numbers, SIN/SSN, GDPR-regulated identifiers, internal credential formats.
- For developer workflows, DLP at the IDE and git level (pre-commit hooks, secret scanners) prevents sensitive data from ever reaching source control.

## Privacy by design

Privacy should be designed in, not bolted on — integrating data protection principles at the architecture and feature design stage rather than as a compliance retrofit:

- **Data minimization** — collect and retain only what you need, for only as long as you need it. Every additional data field collected is a liability.
- **Purpose limitation** — use data only for the purposes disclosed at collection. Building a secondary analytics use case on data collected for operations requires a separate legal basis.
- **Privacy threat modeling** — apply [LINDDUN](https://www.linddun.org/) during design to systematically identify privacy threats (Linkability, Identifiability, Non-repudiation, Detectability, Disclosure, Unawareness, Non-compliance) across data flows and trust boundaries. See [Threat Modeling](../2-Process/2-1-Design/2-1-1-Threat-modeling.md).
- **Privacy regulations** — meet obligations such as GDPR (EU), PIPEDA (Canada), LGPD (Brazil), CCPA (California), and HIPAA (US healthcare), including data-subject rights (access, erasure, portability), lawful basis documentation, and **data residency/sovereignty** requirements — some jurisdictions prohibit transferring personal data outside their borders.

## Protect data across environments

- **Test-data management** — never use real production data in test, dev, or staging environments. Use data masking (obfuscation of real data), anonymization (irreversible de-identification), or synthetic data generation that preserves realistic characteristics without exposing real individuals.
- **Privacy-aware logging** — keep sensitive data out of logs: no passwords, tokens, PII, or full card numbers in application logs, error messages, or distributed traces. See [Logging and Monitoring](../2-Process/2-7-Operate/2-7-2-Logging-and-Monitoring.md).
- **Secure deletion** — verifiably delete data when retention ends. For cloud storage, use crypto-shredding (delete the encryption key) to render data permanently unreadable without re-encrypting the entire dataset.
- **Backup protection** — apply the same encryption and access controls to backups as to primary data. A plaintext backup of an encrypted database is not an encrypted database.
- **AI data handling** — control what data is shared with AI assistants and used for model training. Enterprise data must not flow to third-party AI models without a data processing agreement and privacy review. See [AI Governance and Risk](3-4-AI-Governance-and-Risk.md).

## Maturity progression

**Starter** — data classified manually with basic labels. TLS in transit and at-rest encryption enabled for known sensitive stores. Secrets in a vault. No test-data management policy.

**Intermediate** — automated data discovery and inventory. DLP deployed at key egress points. Privacy threat modeling performed for new features. Formal test-data masking or synthetic data pipeline. Data retention policy defined and partially automated. Privacy reviews gate new data collection.

**Advanced** — real-time data security posture management (DSPM) across all cloud data stores. Crypto-shredding on deletion. E2E encryption for highest-sensitivity data. AI-BOM and data flow mapping for all AI features. All data access audited and anomalies alerted in SIEM. Data minimization enforced by platform defaults.

## Common pitfalls

- **Encrypting everything but managing keys poorly** — encryption is only as strong as key access control. If every service has the decryption key, encryption adds little.
- **Using production data in dev** — one breach of a dev environment that contains real PII is a reportable incident under GDPR and HIPAA.
- **Logging sensitive data "just in case"** — logs are often less protected than primary data stores and retained for long periods. Sensitive data in logs is a recurring breach vector.
- **Forgetting backup data** — backups frequently have weaker access controls, older encryption standards, and longer retention than primary data. They are a high-value, low-visibility target.
- **No data residency enforcement** — data residency requirements are easy to violate when using global cloud services without explicit region constraints.

## Metrics

| Metric | What it tells you |
|---|---|
| % of data stores with at-rest encryption enabled | Baseline encryption coverage |
| % of services enforcing TLS in transit | Network-level confidentiality |
| Key rotation compliance rate | KMS hygiene and operational maturity |
| Data classification coverage (% of stores classified) | Visibility into data landscape |
| Number of DLP policy violations per month (by type) | Volume and nature of exfiltration attempts |
| Time to purge data past retention deadline | Effectiveness of data lifecycle automation |

---

## Tools[^1]

### Open-source

- [Amundsen](https://www.amundsen.io/) — data discovery and metadata catalog to locate and classify sensitive data across a data lake or warehouse. Useful for building an inventory of where sensitive data lives.
- [Presidio](https://github.com/microsoft/presidio) — detects and anonymizes PII (names, credit cards, passport numbers, SSNs, etc.) in text, images, and structured data. Use in data pipelines to scrub PII before loading into non-production environments.
- [Vault](https://www.vaultproject.io/) — secrets management, encryption-as-a-service, and dynamic credentials. Provides a central key management layer across cloud and on-premises infrastructure.

### Commercial

- [BigID](https://bigid.com/) — data discovery, classification, and privacy management across structured and unstructured data. Strong regulatory coverage (GDPR, CCPA, HIPAA) and automated risk scoring.
- [Cyera](https://www.cyera.com/) — data security posture management (DSPM) for cloud environments. Continuously discovers and classifies data, identifies misconfigurations, and prioritizes data exposure risk.
- [Macie (AWS)](https://aws.amazon.com/macie/) — managed ML-based service for discovering and classifying sensitive data in S3. Native integration with AWS security services for alerting and remediation.

---

### Links

[^1]: Listed in alphabetical order.
