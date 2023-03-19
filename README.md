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

- [00-Intro](documents/00-Intro)
  - [00-01-Intro](documents/00-Intro/00-01-Intro.md)
  - [00-02-Overview](documents/00-Intro/00-02-Overview.md)
- [01-Init](documents/01-Init)
  - [01-01-Shape-the-team](documents/01-Init/01-01-Shape-the-team)
    - [01-01-01-Security-champions](documents/01-Init/01-01-Shape-the-team/01-01-01-Security-champions.md)
  - [01-02-Training](documents/01-Init/01-02-Training)
    - [01-02-01-Secure-coding](documents/01-Init/01-02-Training/01-02-01-Secure-coding.md)
    - [01-02-02-Security-CICD](documents/01-Init/01-02-Training/01-02-01-Security-CICD.md)
- [02-Pre-commit](documents/02-Pre-commit)
  - [02-01-Pre-commit](documents/02-Pre-commit/02-01-Pre-commit.md)
  - [02-02-Threat-modeling](documents/02-Pre-commit/02-02-Threat-modeling.md)
  - [02-03-Repository-hardening](documents/02-Pre-commit/02-03-Repository-hardening.md)
  - [02-04-Secrets-Management](documents/02-Pre-commit/02-04-Secrets-Management.md)
  - [02-05-Linting-code](documents/02-Pre-commit/02-05-Linting-code.md)
- [03-Commit-CI](documents/03-Commit-CI)
  - [03-02-Interactive-Application-Security-Testing](documents/03-Commit-CI/03-02-Interactive-Application-Security-Testing.md)
  - [03-01-Static-analysis](documents/03-Commit-CI/03-01-Static-analysis)
    - [03-01-01-Static-Application-Security-Testing](documents/03-Commit-CI/03-01-Static-analysis/03-01-01-Static-Application-Security-Testing.md)
    - [03-01-02-Software-Composition-Analysis](documents/03-Commit-CI/03-01-Static-analysis/03-01-02-Software-Composition-Analysis.md)
    - [03-01-03-Container-Security](documents/03-Commit-CI/03-01-Static-analysis/03-01-03-Container-Security)
      - [03-01-03-01-Container-scanning](documents/03-Commit-CI/03-01-Static-analysis/03-01-03-Container-Security/03-01-03-01-Container-scanning.md)
      - [03-01-03-02-Container-hardening](documents/03-Commit-CI/03-01-Static-analysis/03-01-03-Container-Security/03-01-03-02-Container-hardening.md)
    - [03-01-04-Infastructure-as-code](documents/03-Commit-CI/03-01-Static-analysis/03-01-04-Infastructure-as-code.md)
- [04-Continuous-delivery-CD](documents/04-Continuous-delivery-CD)
  - [04-01-Dynamic-Application-Security-Testing](documents/04-Continuous-delivery-CD/04-01-Dynamic-Application-Security-Testing.md)
  - [04-02-Mobile-Application-Security-Test](documents/04-Continuous-delivery-CD/04-02-Mobile-Application-Security-Test.md)
  - [04-03-API-Security](documents/04-Continuous-delivery-CD/04-03-API-Security.md)
  - [04-04-Miss-Configuration-Check](documents/04-Continuous-delivery-CD/04-04-Miss-Configuration-Check.md)
- [05-Deploy-CD-Golive](documents/05-Deploy-CD-Golive)
  - [05-01-Key-and-certificate-management](documents/05-Deploy-CD-Golive/05-01-Key-and-certificate-management.md)
  - [05-02-Cloud-Native-Application-Protection-Platform](documents/05-Deploy-CD-Golive/05-02-Cloud-Native-Application-Protection-Platform.md)
- [06-Operation](documents/06-Operation)
  - [06-01-Runtime|Continuous-test](documents/06-Operation/06-01-Runtime|Continuous-test)
    - [06-01-01-Infra-scanning](documents/06-Operation/06-01-Runtime|Continuous-test/06-01-01-Infra-scanning)
      - [06-01-01-01-Could-resources](documents/06-Operation/06-01-Runtime|Continuous-test/06-01-01-Infra-scanning/06-01-01-01-Could-resources.md)
      - [06-01-01-02-K8S-resources](documents/06-Operation/06-01-Runtime|Continuous-test/06-01-01-Infra-scanning/06-01-01-02-K8S-resources.md)
    - [06-01-02-Image-scanning](documents/06-Operation/06-01-Runtime|Continuous-test/06-01-02-Image-scanning.md)  
  - [06-02-Breach-and-attack-simulation](documents/06-Operation/06-02-Breach-and-attack-simulation.md)
  - [06-03-Logging-and-Monitoring](documents/06-Operation/06-03-Logging-and-Monitoring.md)
  - [06-04-Pentest](documents/06-Operation/06-04-Pentest.md)
  - [06-05-VDP|Bug-bounty](documents/06-Operation/06-05-VDP|Bug-bounty.md)
- [07-Governance](documents/07-Governance)
  - [07-01-Compliance-Auditing](documents/07-Governance/07-01-Compliance-Auditing)
    - [07-01-01-Compliance-Auditing](documents/07-Governance/07-01-Compliance-Auditing/07-01-01-Compliance-Auditing.md)
    - [07-01-02-Policy-as-code](documents/07-Governance/07-01-Compliance-Auditing/07-01-02-Policy-as-code.md)
    - [07-01-03-Security-benchmarking](documents/07-Governance/07-01-Compliance-Auditing/07-01-03-Security-benchmarking.md)
  - [07-02-Data-protection](documents/07-Governance/07-02-Data-protection.md)
  - [07-03-Reporting](documents/07-Governance/07-03-Reporting)
    - [07-03-01-Tracking-maturities](documents/07-Governance/07-03-Reporting/07-03-01-Tracking-maturities.md)
    - [07-03-02-Central-vulnerability-management-dashboard](documents/07-Governance/07-03-Reporting/07-03-02-Central-vulnerability-management-dashboard.md)



---
The project page on the OWASP website is [here](https://owasp.org/www-project-devsecops-guideline/)
