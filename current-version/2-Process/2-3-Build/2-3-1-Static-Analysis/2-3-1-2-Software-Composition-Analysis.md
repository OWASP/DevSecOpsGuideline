### Software Component/Composition Analysis (SCA)

Software Component Analysis is the process of automating application security for managing third-party and open-source components of the codebase. SCA will find any potentially vulnerable components in our codebase to prevent high-security risks like **Supply-Chain Attack**, not only that but also provide licensing for each component. By doing this, it helps organizations to reduce security risks in their codebase libraries and needs to be early in the modern software development life cycle.

> For more information about the Component Analysis please visit [the OWASP page](https://owasp.org/www-community/Component_Analysis)

We should put the Component Analysis earlier, before security testing like SAST, DAST, and IAST to prevent any vulnerable libraries pushed to live environment (Production) and implemented Continuous Monitoring of its libraries to reduce Supply Chain Attack risk rapidly.

## License Compliance check

TBD

## Supply-Chain Attacks

Supply chain attacks involve exploiting vulnerabilities in the interconnected network of suppliers, vendors, and software components to infiltrate and compromise target systems, often leading to widespread security breaches and data theft. While SCA tools may not directly detect all types of supply chain attacks, they can help mitigate certain risks associated with them. Here's how different types of supply chain attacks can be addressed using SCA:

1. **Dependency Confusion**: Attackers upload malicious packages or libraries to public or private repositories with names similar to legitimate ones. Developers unknowingly install these malicious dependencies, assuming they are safe, leading to security compromises. Example: [PyTorch discloses malicious dependency chain compromise over holidays](https://www.bleepingcomputer.com/news/security/pytorch-discloses-malicious-dependency-chain-compromise-over-holidays/#google_vignette).
SCA tools can detect instances where developers are using dependencies with known vulnerabilities or dependencies that are not declared in the project's configuration files. While they may not directly detect malicious packages, they can alert developers to the presence of unexpected or potentially risky dependencies.

2. **Compromised Build Environments**: Hackers infiltrate build environments or CI/CD pipelines to tamper with the build process, injecting malicious code or altering legitimate code during compilation or packaging stages. Read more here: [10 real-world stories of how we’ve compromised CI/CD pipelines](https://research.nccgroup.com/2022/01/13/10-real-world-stories-of-how-weve-compromised-ci-cd-pipelines/).
SCA tools can analyze the composition of software packages and components used in the build process. By scanning these components for known vulnerabilities or unexpected changes, they can help identify if any malicious code has been injected during the build process.

4. **Software Supply Chain Hijacking**: Attackers compromise the distribution channels of software packages or updates, such as software update servers, download mirrors, or package managers. They replace legitimate software with malicious versions, which are then unwittingly installed by users or organizations. [SolarWinds hack explained](https://www.techtarget.com/whatis/feature/SolarWinds-hack-explained-Everything-you-need-to-know).
  SCA tools can monitor for changes in the integrity of software packages and dependencies. If a legitimate package is replaced with a malicious version, SCA tools can detect the discrepancy and alert developers or security teams.

6. **Counterfeit Components**: Malicious actors create counterfeit hardware or software components that resemble legitimate ones. These counterfeit components may contain hidden vulnerabilities or backdoors, compromising the security of the systems they are integrated into. Stuxnet Worm will fall into this category, [Read more about Stuxnet](https://www.wired.com/2014/11/countdown-to-zero-day-stuxnet/)
While SCA tools may not directly detect counterfeit components, they can help ensure that only trusted and verified components are used in the software development process. By providing visibility into the origin and security status of components, SCA tools can help mitigate the risk of incorporating counterfeit components into software applications.

7. **Third-Party Compromise**:  Hackers compromise third-party vendors or suppliers involved in the software supply chain, gaining access to sensitive information or systems that they can leverage to launch supply chain attacks on their customers or partners.
SCA tools can assess the security posture of third-party vendors or suppliers by analyzing the security of the components they provide. By monitoring for vulnerabilities or unexpected changes in third-party components.
SCA tools can help identify if a third-party vendor has been compromised and alert organizations to the potential risks. [Exploitation of Accellion File Transfer Appliance](https://www.cisa.gov/news-events/cybersecurity-advisories/aa21-055a)

## SBOM

TBD

---

### Tools

- #### Open-source

  - [OWASP Dependency-Track](https://owasp.org/www-project-dependency-track/) - Dependency-Track is an intelligent Component Analysis platform that allows organizations to identify and reduce risk in the software supply chain. It takes a unique and highly beneficial approach by leveraging the capabilities of Software Bill of Materials (SBOM).
  - [OWASP Dependency-check](https://owasp.org/www-project-dependency-check) - Software Composition Analysis (SCA) tool that attempts to detect publicly disclosed vulnerabilities contained within a project’s dependencies and it supports Java, .NET, JavaScript, Ruby
  - [OWASP CycloneDX](https://cyclonedx.org/) - SBOM standard format with many [compatible generators](https://cyclonedx.org/tool-center/) and support for SPDX license IDs and expressions.
  - [OWASP dep-scan](https://owasp.org/www-project-dep-scan/) - Audit tool based on known vulnerabilities for repositories in multiple languages and containers. Generates SBOM and CSAF documents.
  - [RetireJS](https://github.com/RetireJS/retire.js) - JavaScript-specific dependency checker
  - [Safety](https://github.com/pyupio/safety) - Python dependency checker for known security vulnerabilities
  - [bundler-audit](https://github.com/rubysec/bundler-audit) - Patch-level verification for Bundler (Auditing Ruby 3rd party libs versions)

- #### Commercial

  - [Hakiri](https://hakiri.io/) - A commercial tool that offers dependency checking for Ruby and Rails-based GitHub projects using static code analysis
  - [HCL AppScan on Cloud](https://cloud.appscan.com) - SAST tool built as a service that can perform both SAST, SCA & IaC at the same time.
  - [Snyk](https://snyk.io/) - SCA tool offer as a SaaS solution.
  - [WhiteSource](https://www.whitesourcesoftware.com/) - WhiteSource identifies every open source component in your software, including dependencies. It then secures you from vulnerabilities and enforces license policies throughout the software development lifecycle.
  - [Synopsys BlackDuck](https://www.blackducksoftware.com/) - Black Duck automated policy management allows you to define policies for open source use, security risk, and license compliance up front, and automate enforcement across the software development life cycle (SDLC).

### References

- [SCA - OWASP](https://owasp.org/www-community/Component_Analysis)
- [SBOM - OWASP](https://owasp.org/www-community/Component_Analysis#software-bill-of-materials-sbom)
