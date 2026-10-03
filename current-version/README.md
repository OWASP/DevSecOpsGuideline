# OWASP DevSecOps Guideline

This is the current version of the OWASP DevSecOps Guideline. It explains how to build and operate a secure software delivery pipeline, promotes a **shift-left** (shift-everywhere) security culture, and curates vendor-neutral practices and tools for organizations of any size.

The guideline is organized around the three core pillars of DevSecOps:

- **People** — teams, roles, culture, and training.
- **Process** — security activities woven into every stage of the software development lifecycle.
- **Governance** — compliance, measurement, reporting, and oversight.

Under **Process**, the product development lifecycle is divided into seven stages: **Design, Develop, Build, Test, Release, Deploy, Operate** — with security controls mapped to each.

![DevSecOps Pillars](/current-version/assets/images/devsecops-pillars.png)

This revision refreshes every topic for 2025/2026 and adds coverage of modern concerns: software supply-chain security (SBOM, signing/provenance, CI/CD pipeline security), AI-assisted development and AI governance, Application Security Posture Management (ASPM), and explicit alignment with frameworks such as NIST SSDF, OWASP SAMM, OWASP DSOMM, and SLSA.

If you need earlier editions, see the [old-versions](../old-versions/) directory.

## Table of Contents

- [0-Intro](0-Intro)
  - [0-1-Intro](0-Intro/0-1-Intro.md)
  - [0-2-Overview](0-Intro/0-2-Overview.md)
  - [0-3-Frameworks-and-Standards](0-Intro/0-3-Frameworks-and-Standards.md)
- [1-People](1-People)
  - [1-1-Shape-the-team](1-People/1-1-Shape-the-team)
    - [1-1-1-Security-champions](1-People/1-1-Shape-the-team/1-1-1-Security-champions.md)
    - [1-1-2-Roles-and-Responsibilities](1-People/1-1-Shape-the-team/1-1-2-Roles-and-Responsibilities.md)
  - [1-2-Training](1-People/1-2-Training)
    - [1-2-1-Secure-coding](1-People/1-2-Training/1-2-1-Secure-coding.md)
    - [1-2-2-Security-CICD](1-People/1-2-Training/1-2-2-Security-CICD.md)
    - [1-2-3-Security-culture-and-awareness](1-People/1-2-Training/1-2-3-Security-culture-and-awareness.md)
- [2-Process](2-Process)
  - [2-1-Design](2-Process/2-1-Design)
    - [2-1-1-Threat-modeling](2-Process/2-1-Design/2-1-1-Threat-modeling.md)
    - [2-1-2-Secure-design-and-requirements](2-Process/2-1-Design/2-1-2-Secure-design-and-requirements.md)
  - [2-2-Develop](2-Process/2-2-Develop)
    - [2-2-1-Pre-commit](2-Process/2-2-Develop/2-2-1-Pre-commit)
      - [2-2-1-1-Pre-commit](2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-1-Pre-commit.md)
      - [2-2-1-2-Secrets-Management](2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md)
      - [2-2-1-3-Linting-code](2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-3-Linting-code.md)
      - [2-2-1-4-Repository-Hardening](2-Process/2-2-Develop/2-2-1-Pre-commit/2-2-1-4-Repository-Hardening.md)
    - [2-2-2-IDE-and-AI-assisted-development](2-Process/2-2-Develop/2-2-2-IDE-and-AI-assisted-development.md)
  - [2-3-Build](2-Process/2-3-Build)
    - [2-3-1-Static-Analysis](2-Process/2-3-Build/2-3-1-Static-Analysis)
      - [2-3-1-1-Static-Application-Security-Testing](2-Process/2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md)
    - [2-3-2-Software-Composition-Analysis](2-Process/2-3-Build/2-3-2-Software-Composition-Analysis)
      - [2-3-2-1-Software-Composition-Analysis](2-Process/2-3-Build/2-3-2-Software-Composition-Analysis/2-3-2-1-Software-Composition-Analysis.md)
    - [2-3-3-Container-Security](2-Process/2-3-Build/2-3-3-Container-Security)
      - [2-3-3-1-Container-Scanning](2-Process/2-3-Build/2-3-3-Container-Security/2-3-3-1-Container-Scanning.md)
      - [2-3-3-2-Container-Hardening](2-Process/2-3-Build/2-3-3-Container-Security/2-3-3-2-Container-Hardening.md)
    - [2-3-4-Infrastructure-as-Code-Security](2-Process/2-3-Build/2-3-4-Infrastructure-as-Code-Security)
      - [2-3-4-1-Infrastructure-as-Code-Scanning](2-Process/2-3-Build/2-3-4-Infrastructure-as-Code-Security/2-3-4-1-Infrastructure-as-Code-Scanning.md)
    - [2-3-5-Security-Gates](2-Process/2-3-Build/2-3-5-Security-Gates.md)
    - [2-3-6-Supply-Chain-Security](2-Process/2-3-Build/2-3-6-Supply-Chain-Security)
      - [2-3-6-1-SBOM](2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-1-SBOM.md)
      - [2-3-6-2-Artifact-Signing-and-Provenance](2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-2-Artifact-Signing-and-Provenance.md)
      - [2-3-6-3-CICD-Pipeline-Security](2-Process/2-3-Build/2-3-6-Supply-Chain-Security/2-3-6-3-CICD-Pipeline-Security.md)
  - [2-4-Test](2-Process/2-4-Test)
    - [2-4-1-Interactive-Application-Security-Testing](2-Process/2-4-Test/2-4-1-Interactive-Application-Security-Testing.md)
    - [2-4-2-Dynamic-Application-Security-Testing](2-Process/2-4-Test/2-4-2-Dynamic-Application-Security-Testing.md)
    - [2-4-3-Mobile-Application-Security-Test](2-Process/2-4-Test/2-4-3-Mobile-Application-Security-Test.md)
    - [2-4-4-API-Security](2-Process/2-4-Test/2-4-4-API-Security.md)
    - [2-4-5-Misconfiguration-Check](2-Process/2-4-Test/2-4-5-Misconfiguration-Check.md)
  - [2-5-Release](2-Process/2-5-Release)
    - [2-5-1-Release](2-Process/2-5-Release/2-5-1-Release.md)
  - [2-6-Deploy](2-Process/2-6-Deploy)
    - [2-6-1-Deploy](2-Process/2-6-Deploy/2-6-1-Deploy.md)
  - [2-7-Operate](2-Process/2-7-Operate)
    - [2-7-1-Cloud-Native-Security](2-Process/2-7-Operate/2-7-1-Cloud-Native-Security.md)
    - [2-7-2-Logging-and-Monitoring](2-Process/2-7-Operate/2-7-2-Logging-and-Monitoring.md)
    - [2-7-3-Pentest](2-Process/2-7-Operate/2-7-3-Pentest.md)
    - [2-7-4-Vulnerability-Management](2-Process/2-7-Operate/2-7-4-Vulnerability-Management.md)
    - [2-7-5-VDP-and-Bug-bounty](2-Process/2-7-Operate/2-7-5-VDP-and-Bug-bounty.md)
    - [2-7-6-Breach-and-attack-simulation](2-Process/2-7-Operate/2-7-6-Breach-and-attack-simulation.md)
- [3-Governance](3-Governance)
  - [3-1-Compliance-Auditing](3-Governance/3-1-Compliance-Auditing)
    - [3-1-1-Compliance-Auditing](3-Governance/3-1-Compliance-Auditing/3-1-1-Compliance-Auditing.md)
    - [3-1-2-Policy-as-code](3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md)
    - [3-1-3-Security-benchmarking](3-Governance/3-1-Compliance-Auditing/3-1-3-Security-benchmarking.md)
  - [3-2-Data-protection](3-Governance/3-2-Data-protection.md)
  - [3-3-Reporting](3-Governance/3-3-Reporting)
    - [3-3-1-Tracking-maturities](3-Governance/3-3-Reporting/3-3-1-Tracking-maturities.md)
    - [3-3-2-Central-vulnerability-management-dashboard](3-Governance/3-3-Reporting/3-3-2-Central-vulnerability-management-dashboard.md)
    - [3-3-3-ASPM](3-Governance/3-3-Reporting/3-3-3-ASPM.md)
  - [3-4-AI-Governance-and-Risk](3-Governance/3-4-AI-Governance-and-Risk.md)
