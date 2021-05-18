## Interactive Application Security Testing

**IAST (interactive application security testing)** is an application security testing method that tests the application while the app is run by an automated test, human tester, or any activity “interacting” with the application functionality.

The core of an IAST tool is sensor modules, software libraries included in the application code. These sensor modules keep track of application behavior while the interactive tests are running. If a vulnerability is detected, an alert will be sent.

The process and feedback are done in real time in your integrated development environment (IDE), continuous integration (CI) environment, or quality assurance, or while in production. The sensors have access to:
+ Entire code
+ Dataflow and control flow
+ System configuration data
+ Web components
+ Back-end connection data

Examples of such vulnerabilities could be hardcoding API keys in cleartext, not sanitizing your users inputs, or using connections without SSL encryption.

---

### IAST vs SAST

**Static Application Security Testing** method examine source code in a non-runtime environment early in the SDLC. They look for suspicious code patterns that indicate security risks. Even though they are easy to deploy, SASTs throw too many false positives because SASTs do not take into account the presence of other security countermeasures, and they lack visibility during runtime. SAST tools normally run inside the IDE as part of the compilation phase, and introduce delays as the scan process takes time to finish. IASTs are more flexible than SASTs, because they are applicable in production runtime environments (SASTs require direct access to the source code).

### IAST vs DAST

**Dynamic Application Security Testing** method is works like a black-box scanner that executes requests against the application to find security issues. DASTs look at the applications from the exterior and determine the presence of risks by looking at the response (including body and headers) of the server to a battery of tests, but DASTs have no visibility of the internal workings of the app. Furthermore, DAST tests are hard to automate, because DASTs must be operated by experienced appsec teams, such as penetration testers, to be truly useful. Forrester estimates that the duration of a DAST scan can take around 5 to 7 days, while testing with IAST is a real-time (zero minutes) operation.

---

### Tools

+ [Contrast Community Edition (CE)](https://www.contrastsecurity.com/contrast-community-edition)
+ [Checkmarx Interactive Application Security Testing(CxIAST)](https://www.checkmarx.com/products/interactive-application-security-testing/)
+ [Seeker Interactive Application Security Testing](https://www.synopsys.com/software-integrity/security-testing/interactive-application-security-testing.html)

---

### References

+ [Veracode - IAST](https://www.veracode.com/security/interactive-application-security-testing-iast)
+ [OWASP - Free for Open Source Application Security Tools](https://owasp.org/www-community/Free_for_Open_Source_Application_Security_Tools)
+ [Hdivsecurity - IAST](https://hdivsecurity.com/bornsecure/what-is-iast-interactive-application-security-testing/)
+ [Contrastsecurity - IAST](https://www.contrastsecurity.com/knowledge-hub/glossary/interactive-application-security-testing)
+ [Synk - IAST](https://snyk.io/learn/iast-interactive-application-security-testing/)
+ [Acunetix - IAST](https://www.acunetix.com/blog/web-security-zone/what-is-iast-interactive-application-security-testing/)
+ [Contrast - Why the difference sast, dast, and iast mastters](https://www.contrastsecurity.com/security-influencers/why-the-difference-between-sast-dast-and-iast-matters)
+ [Esecurityplanet - Application security vendors](https://www.esecurityplanet.com/products/application-security-vendors/)