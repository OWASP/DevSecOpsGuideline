# OWASP DevSecOps Guideline
The OWASP DevSecOps Guideline explains how we can implement a secure pipeline and use best practices and introduce tools that we can use in this matter. Also, the project is trying to help us promote the shift-left security culture in our development process.  
This project helps any companies of each size that have a development pipeline or, in other words, have a DevOps pipeline.
We try to draw a perspective of a secure DevOps pipeline during this project and then improve it based on our customized requirements.  

The Ideal goal is **"detect security issues (by design or application vulnerability) as early as possible."**

## Initial steps
DevSecOps is all about putting security into DevOps. But to keep up with the pace of CI/CD, security has to be injected early into software writing and testing.

![DevSecOps cycle](/assets/images/DevSecOps-cycle.png)

[OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/) lists the top 10 security controls every developer has to implement while coding any application. Consider this set as the starting point when you have to design, write or test code in the DevSecOps cycle. 

You can also follow the [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/model/) to establish what to consider for security requirements (and more) according to your maturity level.

## What to add in a pipeline
![DevSecOps pipeline](/assets/images/DevSecOps-pipeline.png)
At first, we consider implementing the following steps in a basic pipeline:
* Scan git repositories for finding potential credentials leakage. 
* SCA (Software Composition Analysis)
* SAST (Static Application Security Test)
* IaC Scanning (Scanning Terraform, HelmChart code to find misconfiguration)
* IAST (Interactive Application Security Testing)
* API Security
* DAST (Dynamic Application Security Test)
* CNAPP (Cloud Native Application Protection)
* Infrastructure scanning
* Continuous Scanning from other tools
* Compliance check

We can customize the steps of our pipeline according to our Software Development Life Cycle (SDLC) or software architecture and add automation progressively if we are starting.
For instance, we can switch from SAST/DAST to a regular test suite with built-in security controls or add an audit script checking for known vulnerable dependencies.

CI/CD is an advantage for SecOps, a privileged entry point for security measures and controls.
However, when using CI/CD tools to provide automation, keep in mind that the tools themselves often expand your attack surface, so put security controls on building, deployment, and automation software.

---
## Table of Contents:
- [0-Intro](current-version/0-Intro)
  - [0-1-Intro](current-version/0-Intro/0-1-Intro.md)
  - [0-2-Overview](current-version/0-Intro/0-2-Overview.md)
- [1-People](current-version/1-People)
  - [1-1-Shape-the-team](current-version/1-People/1-1-Shape-the-team)
    - [1-1-1-Security-champions](current-version/1-People/1-1-Shape-the-team/1-1-1-Security-champions.md)
  - [1-2-Training](current-version/1-People/1-2-Training)
    - [1-2-1-Secure-coding](current-version/1-People/1-2-Training/1-2-1-Secure-coding.md)
    - [1-2-2-Security-CICD](current-version/1-People/1-2-Training/1-2-2-Security-CICD.md)
- [2-Process](current-version/2-Process)
  - [2-1-Design](current-version/2-Process/2-1-Design)
    - [2-1-1-Threat-modeling](current-version/2-Process/2-1-Design/2-1-1-Threat-modeling.md)
  - [2-2-Code](current-version/2-Process/2-2-Code)
    - [2-2-3-Interactive-Application-Security-Testing](current-version/2-Process/2-2-Code/2-2-3-Interactive-Application-Security-Testing.md)
    - [2-2-1-Pre-commit](current-version/2-Process/2-2-Code/2-2-1-Pre-commit)
      - [2-2-1-1-Pre-commit](current-version/2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-1-Pre-commit.md)
      - [2-2-1-2-Secrets-Management](current-version/2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-2-Secrets-Management.md)
      - [2-2-1-3-Linting-code](current-version/2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-3-Linting-code.md)
      - [2-2-1-4-Repository-Hardening](current-version/2-Process/2-2-Code/2-2-1-Pre-commit/2-2-1-4-Repository-Hardening.md)
    - [2-2-2-Static-Analysis](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis)
      - [2-2-2-1-Static-Application-Security-Testing](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-1-Static-Application-Security-Testing.md)
      - [2-2-2-2-Software-Composition-Analysis](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-2-Software-Composition-Analysis.md)
      - [2-2-2-3-Infastructure-as-Code-Scanning](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-3-Infastructure-as-Code-Scanning.md)
      - [2-2-2-4-Container-Security](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security)
        - [2-2-2-4-1-Container-Scanning](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security/2-2-2-4-1-Container-Scanning.md)
        - [2-2-2-4-2-Container-Hardening](current-version/2-Process/2-2-Code/2-2-2-Static-Analysis/2-2-2-4-Container-Security/2-2-2-4-2-Container-Hardening.md)
  - [2-3-Build](current-version/2-Process/2-3-Build)
    - [2-3-1-Dynamic-Application-Security-Testing](current-version/2-Process/2-3-Build/2-3-1-Dynamic-Application-Security-Testing.md)
    - [2-3-2-Mobile-Application-Security-Test](current-version/2-Process/2-3-Build/2-3-2-Mobile-Application-Security-Test.md)
    - [2-3-3-API-Security](current-version/2-Process/2-3-Build/2-3-3-API-Security.md)
    - [2-3-4-Miss-Configuration-Check](current-version/2-Process/2-3-Build/2-3-4-Miss-Configuration-Check.md)
  - [2-4-Operation](current-version/2-Process/2-4-Operation)
    - [2-4-1-Cloud-Native-Security](current-version/2-Process/2-4-Operation/2-4-1-Cloud-Native-Security.md)
    - [2-4-2-Logging-and-Monitoring](current-version/2-Process/2-4-Operation/2-4-2-Logging-and-Monitoring.md)
    - [2-4-3-Pentest](current-version/2-Process/2-4-Operation/2-4-3-Pentest.md)
    - [2-4-4-Vulnerability-Management](current-version/2-Process/2-4-Operation/2-4-4-Vulnerability-Management.md)
    - [2-4-5-VDP|Bug-bounty](current-version/2-Process/2-4-Operation/2-4-5-VDP|Bug-bounty.md)
    - [2-4-6-Breach-and-attack-simulation](current-version/2-Process/2-4-Operation/2-4-6-Breach-and-attack-simulation.md)
- [3-Governance](current-version/3-Governance)
  - [3-2-Data-protection](current-version/3-Governance/3-2-Data-protection.md)
  - [3-1-Compliance-Auditing](current-version/3-Governance/3-1-Compliance-Auditing)
    - [3-1-1-Compliance-Auditing](current-version/3-Governance/3-1-Compliance-Auditing/3-1-1-Compliance-Auditing.md)
    - [3-1-2-Policy-as-code](current-version/3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md)
    - [3-1-3-Security-benchmarking](current-version/3-Governance/3-1-Compliance-Auditing/3-1-3-Security-benchmarking.md)
  - [3-3-Reporting](current-version/3-Governance/3-3-Reporting)
    - [3-3-1-Tracking-maturities](current-version/3-Governance/3-3-Reporting/3-3-1-Tracking-maturities.md)
    - [3-3-2-Central-vulnerability-management-dashboard](current-version/3-Governance/3-3-Reporting/3-3-2-Central-vulnerability-management-dashboard.md)


---
The project page on the OWASP website is [here](https://owasp.org/www-project-devsecops-guideline/)
