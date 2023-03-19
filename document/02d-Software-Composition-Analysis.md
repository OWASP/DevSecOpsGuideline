### Software Component/Composition Analysis (SCA)

Software Component Analysis is the process of automating application security for managing third-party and open source components of codebase. SCA will find any potential vulnerable components in our codebase to prevent high security risks like **Supply-Chain Attack**, not only that but also provide licensing about each components. By doing this, it helps organization to reduce security risks in their codebase libraries and needed to be early in modern software development life cycle.

> For more information about the Component Analysis please visit [the OWASP page](https://owasp.org/www-community/Component_Analysis)

We should put the Component Analysis earlier, before security testing like SAST, DAST, and IAST to prevent any vulnerable libraries pushed to live environment (Production) and implemented Continuous Monitoring of its libraries to reduce Supply Chain Attack risk rapidly.

---
### Tools
- #### Open-source:
  + [OWASP Dependency-check](https://owasp.org/www-project-dependency-check) - Software Composition Analysis (SCA) tool that attempts to detect publicly disclosed vulnerabilities contained within a project’s dependencies and it supports Java, .NET, JavaScript, Ruby
  + [OWASP Dependency-Track](https://owasp.org/www-project-dependency-track/) - Dependency-Track is an intelligent Component Analysis platform that allows organizations to identify and reduce risk in the software supply chain. It takes a unique and highly beneficial approach by leveraging the capabilities of Software Bill of Materials (SBOM).
  + [RetireJS](https://github.com/RetireJS/retire.js) - JavaScript-specific dependency checker
  + [Safety](https://github.com/pyupio/safety) - Python dependency checker for known security vulnerabilities
  + [bundler-audit](https://github.com/rubysec/bundler-audit) - Patch-level verification for Bundler (Auditing Ruby 3rd party libs versions)

- #### Commercial:
  + [Hakiri](https://hakiri.io/) - A commercial tool that offers dependency checking for Ruby and Rails-based GitHub projects using static code analysis
  + [HCL AppScan on Cloud](https://cloud.appscan.com) - SAST tool built as a service that can perform both SAST, SCA & IaC at the same time. 
  + [Snyk](https://snyk.io/) - SCA tool offer as a SaaS solution. 
  + [WhiteSource](https://www.whitesourcesoftware.com/) - WhiteSource identifies every open source component in your software, including dependencies. It then secures you from vulnerabilities and enforces license policies throughout the software development lifecycle.
  + [Synopsys BlackDuck](https://www.blackducksoftware.com/) - Black Duck automated policy management allows you to define policies for open source use, security risk, and license compliance up front, and automate enforcement across the software development life cycle (SDLC).


### References

+ [SCA - OWASP](https://owasp.org/www-community/Component_Analysis)
+ [SBOM - CISA](https://www.cisa.gov/sbom#:~:text=A%20%E2%80%9Csoftware%20bill%20of%20materials,that%20make%20up%20software%20components.)
