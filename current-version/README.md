# OWASP DevSecOps Guideline

This is the updated version of the DevSecOps Guideline. In this version, we have revised our documentation approach to provide a more structured format. The primary focus of this restructuring was on the core pillars of DevSecOps, which include:
- People
- Process
- Governance

Under the Process section, we have conducted a detailed examination of the product development process and have divided it into the following seven steps:
- Design
- Develop
- Build
- Test
- Release
- Deploy
- Operate  

The following image can illustrate it better.  

![DevSecOps Pillars](/current-version/assets/images/devsecops-pillars.png)

If you need the old verions please check [old-versions](../old-versions/) directory.

## Table of Contents:

- [0-Intro](0-Intro)
  - [0-1-Intro](0-Intro/0-1-Intro.md)
  - [0-2-Overview](0-Intro/0-2-Overview.md)
- [1-People](1-People)
  - [1-1-Shape-the-team](1-People/1-1-Shape-the-team)
    - [1-1-1-Security-champions](1-People/1-1-Shape-the-team/1-1-1-Security-champions.md)
  - [1-2-Training](1-People/1-2-Training)
    - [1-2-1-Secure-coding](1-People/1-2-Training/1-2-1-Secure-coding.md)
    - [1-2-2-Security-CICD](1-People/1-2-Training/1-2-2-Security-CICD.md)
- [2-Process](2-Process)
  - [2-1-Design](2-Process/2-1-Design)
    - [2-1-1-Threat-modeling](2-Process/2-1-Design/2-1-1-Threat-modeling.md)
  - [2-2-Code](2-Process/2-2-Code)
    - [2-2-3-Interactive-Application-Security-Testing](2-Process/2-2-Code/2-2-3-Interactive-Application-Security-Testing.md)
    - [2-2-1-Pre-commit](2-Process/2-2-Code/2-2-1-Pre-commit)
      - [2-2-1-1-Pre-commit](2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-1-Pre-commit.md)
      - [2-2-1-2-Secrets-Management](2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md)
      - [2-2-1-3-Linting-code](2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-3-Linting-code.md)
      - [2-2-1-4-Repository-Hardening](2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-4-Repository-Hardening.md)
    - [2-2-2-Static-Analysis](2-Process/2-2-Code/2-2-2-Static-Analysis)
      - [2-2-2-1-Static-Application-Security-Testing](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-1-Static-Application-Security-Testing.md)
      - [2-2-2-2-Software-Composition-Analysis](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-2-Software-Composition-Analysis.md)
      - [2-2-2-3-Infastructure-as-Code-Scanning](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-3-Infastructure-as-Code-Scanning.md)
      - [2-2-2-4-Container-Security](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security)
        - [2-2-2-4-1-Container-Scanning](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security/2-2-2-4-1-Container-Scanning.md)
        - [2-2-2-4-2-Container-Hardening](2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security/2-2-2-4-2-Container-Hardening.md)
  - [2-3-Build](2-Process/2-3-Build)
    - [2-3-1-Dynamic-Application-Security-Testing](2-Process/2-3-Build/2-3-1-Dynamic-Application-Security-Testing.md)
    - [2-3-2-Mobile-Application-Security-Test](2-Process/2-3-Build/2-3-2-Mobile-Application-Security-Test.md)
    - [2-3-3-API-Security](2-Process/2-3-Build/2-3-3-API-Security.md)
    - [2-3-4-Miss-Configuration-Check](2-Process/2-3-Build/2-3-4-Miss-Configuration-Check.md)
  - [2-4-Operation](2-Process/2-4-Operation)
    - [2-4-1-Cloud-Native-Security](2-Process/2-4-Operation/2-4-1-Cloud-Native-Security.md)
    - [2-4-2-Logging-and-Monitoring](2-Process/2-4-Operation/2-4-2-Logging-and-Monitoring.md)
    - [2-4-3-Pentest](2-Process/2-4-Operation/2-4-3-Pentest.md)
    - [2-4-4-Vulnerability-Management](2-Process/2-4-Operation/2-4-4-Vulnerability-Management.md)
    - [2-4-5-VDP|Bug-bounty](2-Process/2-4-Operation/2-4-5-VDP|Bug-bounty.md)
    - [2-4-6-Breach-and-attack-simulation](2-Process/2-4-Operation/2-4-6-Breach-and-attack-simulation.md)
- [3-Governance](3-Governance)
  - [3-2-Data-protection](3-Governance/3-2-Data-protection.md)
  - [3-1-Compliance-Auditing](3-Governance/3-1-Compliance-Auditing)
    - [3-1-1-Compliance-Auditing](3-Governance/3-1-Compliance-Auditing/3-1-1-Compliance-Auditing.md)
    - [3-1-2-Policy-as-code](3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md)
    - [3-1-3-Security-benchmarking](3-Governance/3-1-Compliance-Auditing/3-1-3-Security-benchmarking.md)
  - [3-3-Reporting](3-Governance/3-3-Reporting)
    - [3-3-1-Tracking-maturities](3-Governance/3-3-Reporting/3-3-1-Tracking-maturities.md)
    - [3-3-2-Central-vulnerability-management-dashboard](3-Governance/3-3-Reporting/3-3-2-Central-vulnerability-management-dashboard.md)
