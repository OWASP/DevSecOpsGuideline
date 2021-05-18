### Software Component/Composition Analysis (SCA)

Component Analysis is the process of automating application security for managing third-party and open source components of codebase. SCA will find any potential vulnerable components in our codebase to prevent high security risks like **Supply-Chain Attack**, not only that but also provide licensing about each components. By doing this, it helps organization to reduce security risks in their codebase libraries and needed to be early in modern software development life cycle.

> For more information about the Component Analysis please visit [the OWASP page](https://owasp.org/www-community/Component_Analysis)

We should put the Component Analysis earlier, before security testing like SAST, DAST to prevent any vulnerable libraries pushed to live environment (Production) and implemented Continuous Monitoring of its libraries to reduce Supply Chain Attack risk rapidly.

---
### Tools
- #### Open-source:
  + [OWASP Dependency-check](https://owasp.org/www-project-dependency-check) - Software Composition Analysis (SCA) tool that attempts to detect publicly disclosed vulnerabilities contained within a project’s dependencies and it supports Java, .NET, JavaScript, Ruby
  + [RetireJS](https://github.com/RetireJS/retire.js) - JavaScript-specific dependency checker
  + [Safety](https://github.com/pyupio/safety) - Python dependency checker for known security vulnerabilities
  + [bundler-audit](https://github.com/rubysec/bundler-audit) - Patch-level verification for Bundler (Auditing Ruby 3rd party libs versions)

- #### Commercial:
  + [Hakiri](https://hakiri.io/) - A commercial tool that offers dependency checking for Ruby and Rails-based GitHub projects using static code analysis


### References

+ [SCA - OWASP](https://owasp.org/www-community/Component_Analysis)