# OWASP DevSecOps Guideline
The OWASP DevSecOps Guideline explains how we can implement a secure pipeline and use best practices and introduce tools that we can use in this matter. Also, the project is trying to help us promote the shift-left security culture in our development process.  
This project helps any companies of each size that have a development pipeline or, in other words, have a DevOps pipeline.
We try to draw a perspective of a secure DevOps pipeline during this project and then improve it based on our customized requirements.  

The Ideal goal is **"detect security issues (by design or application vulnerability) as fast as possible."**

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

- [0-Intro](documents/0-Intro)
  - [0-1-Intro](documents/0-Intro/0-1-Intro.md)
  - [0-2-Overview](documents/0-Intro/0-2-Overview.md)
- [1-Init](documents/1-Init)
  - [1-1-Shape-the-team](documents/1-Init/1-1-Shape-the-team)
    - [1-1-1-Security-champions](documents/1-Init/1-1-Shape-the-team/1-1-1-Security-champions.md)
  - [1-2-Training](documents/1-Init/1-2-Training)
    - [1-2-1-Secure-coding](documents/1-Init/1-2-Training/1-2-1-Secure-coding.md)
    - [1-2-2-Security-CICD](documents/1-Init/1-2-Training/1-2-1-Security-CICD.md)
- [2-Pre-commit](documents/2-Pre-commit)
  - [2-1-Pre-commit](documents/2-Pre-commit/2-1-Pre-commit.md)
  - [2-2-Threat-modeling](documents/2-Pre-commit/2-2-Threat-modeling.md)
  - [2-3-Repository-hardening](documents/2-Pre-commit/2-3-Repository-hardening.md)
  - [2-4-Secrets-Management](documents/2-Pre-commit/2-4-Secrets-Management.md)
  - [2-5-Linting-code](documents/2-Pre-commit/2-5-Linting-code.md)
- [3-Commit-CI](documents/3-Commit-CI)
  - [3-2-Interactive-Application-Security-Testing](documents/3-Commit-CI/3-2-Interactive-Application-Security-Testing.md)
  - [3-1-Static-analysis](documents/3-Commit-CI/3-1-Static-analysis)
    - [3-1-1-Static-Application-Security-Testing](documents/3-Commit-CI/3-1-Static-analysis/3-1-1-Static-Application-Security-Testing.md)
    - [3-1-2-Software-Composition-Analysis](documents/3-Commit-CI/3-1-Static-analysis/3-1-2-Software-Composition-Analysis.md)
    - [3-1-3-Container-Security](documents/3-Commit-CI/3-1-Static-analysis/3-1-3-Container-Security)
      - [3-1-3-1-Container-scanning](documents/3-Commit-CI/3-1-Static-analysis/3-1-3-Container-Security/3-1-3-1-Container-scanning.md)
      - [3-1-3-2-Container-hardening](documents/3-Commit-CI/3-1-Static-analysis/3-1-3-Container-Security/3-1-3-2-Container-hardening.md)
    - [3-1-4-Infastructure-as-code](documents/3-Commit-CI/3-1-Static-analysis/3-1-4-Infastructure-as-code.md)
- [4-Continuous-delivery-CD](documents/4-Continuous-delivery-CD)
  - [4-1-Dynamic-Application-Security-Testing](documents/4-Continuous-delivery-CD/4-1-Dynamic-Application-Security-Testing.md)
  - [4-2-Mobile-Application-Security-Test](documents/4-Continuous-delivery-CD/4-2-Mobile-Application-Security-Test.md)
  - [4-3-API-Security](documents/4-Continuous-delivery-CD/4-3-API-Security.md)
  - [4-4-Miss-Configuration-Check](documents/4-Continuous-delivery-CD/4-4-Miss-Configuration-Check.md)
- [5-Deploy-CD-Golive](documents/5-Deploy-CD-Golive)
  - [5-1-Key-and-certificate-management](documents/5-Deploy-CD-Golive/5-1-Key-and-certificate-management.md)
  - [5-2-Cloud-Native-Application-Protection-Platform](documents/5-Deploy-CD-Golive/5-2-Cloud-Native-Application-Protection-Platform.md)
- [6-Operation](documents/6-Operation)
  - [6-1-Runtime|Continuous-test](documents/6-Operation/6-1-Runtime|Continuous-test)
    - [6-1-1-Infra-scanning](documents/6-Operation/6-1-Runtime|Continuous-test/6-1-1-Infra-scanning)
      - [6-1-1-1-Could-resources](documents/6-Operation/6-1-Runtime|Continuous-test/6-1-1-Infra-scanning/6-1-1-1-Could-resources.md)
      - [6-1-1-2-K8S-resources](documents/6-Operation/6-1-Runtime|Continuous-test/6-1-1-Infra-scanning/6-1-1-2-K8S-resources.md)
    - [6-1-2-Image-scanning](documents/6-Operation/6-1-Runtime|Continuous-test/6-1-2-Image-scanning.md)  
  - [6-2-Breach-and-attack-simulation](documents/6-Operation/6-2-Breach-and-attack-simulation.md)
  - [6-3-Logging-and-Monitoring](documents/6-Operation/6-3-Logging-and-Monitoring.md)
  - [6-4-Pentest](documents/6-Operation/6-4-Pentest.md)
  - [6-5-VDP|Bug-bounty](documents/6-Operation/6-5-VDP|Bug-bounty.md)
- [7-Governance](documents/7-Governance)
  - [7-1-Compliance-Auditing](documents/7-Governance/7-1-Compliance-Auditing)
    - [7-1-1-Compliance-Auditing](documents/7-Governance/7-1-Compliance-Auditing/7-1-1-Compliance-Auditing.md)
    - [7-1-2-Policy-as-code](documents/7-Governance/7-1-Compliance-Auditing/7-1-2-Policy-as-code.md)
    - [7-1-3-Security-benchmarking](documents/7-Governance/7-1-Compliance-Auditing/7-1-3-Security-benchmarking.md)
  - [7-2-Data-protection](documents/7-Governance/7-2-Data-protection.md)
  - [7-3-Reporting](documents/7-Governance/7-3-Reporting)
    - [7-3-1-Tracking-maturities](documents/7-Governance/7-3-Reporting/7-3-1-Tracking-maturities.md)
    - [7-3-2-Central-vulnerability-management-dashboard](documents/7-Governance/7-3-Reporting/7-3-2-Central-vulnerability-management-dashboard.md)



---
The project page on the OWASP website is [here](https://owasp.org/www-project-devsecops-guideline/)
