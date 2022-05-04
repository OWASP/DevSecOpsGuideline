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
* SAST (Static Application Security Test)
* SCA (Software Composition Analysis)
* IAST (Interactive Application Security Testing)
* DAST (Dynamic Application Security Test)
* IaC Scanning (Scanning Terraform, HelmChart code to find misconfiguration)
* Infrastructure scanning
* Compliance check

We can customize the steps of our pipeline according to our Software Development Life Cycle (SDLC) or software architecture and add automation progressively if we are starting.
For instance, we can switch from SAST/DAST to a regular test suite with built-in security controls or add an audit script checking for known vulnerable dependencies.

CI/CD is an advantage for SecOps, a privileged entry point for security measures and controls.
However, when using CI/CD tools to provide automation, keep in mind that the tools themselves often expand your attack surface, so put security controls on building, deployment, and automation software.

---
The project page on the OWASP website is [here](https://owasp.org/www-project-devsecops-guideline/)