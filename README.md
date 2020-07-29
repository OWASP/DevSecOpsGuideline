# OWASP DevSecOps Guideline
The OWASP DevSecOps Guideline focuses on explaining how we can implement a secure pipeline and using best practices and introduce tools that we can use in this matter. Also, the project trying to help us for promoting the shift-left security culture in our development process.  
This project helps any companies in each size that have development pipeline or in other words have DevOps pipeline.
During this project, we try to draw a perspective of a secure DevOps pipeline and then improve it based on our customized requirements.

## Initial steps
DevSecOps is all about putting security into DevOps. But to keep up with the pace of CI/CD security has to be injected early, into software writing and testing.

![DevSecOps cycle](/assets/images/DevSecOps-cycle.png)

[OWASP Proactive Controls](https://owasp.org/www-project-proactive-controls/) lists the top 10 security controls every developer has to follow while coding any application. Consider this set as the starting point when you have to design, write or test code in the DevSecOps cycle. 

You can also follow the [OWASP Software Assurance Maturity Model (SAMM)](https://owaspsamm.org/model/) to establish what actions to consider as security requirements according to your maturity level.

### What to add in a pipeline
![DevSecOps pipeline](/assets/images/DevSecOps-pipeline.png)
At first, we consider to implement the following steps in a basic pipeline:
* Take care secrets and credentials in git repositories
* SAST (Static Application Security Test)
* DAST (Dynamic Application Security Test)
* Infrastructure scanning
* Compliance check

---
The project page in OWASP website is [here](https://owasp.org/www-project-devsecops-guideline/)
