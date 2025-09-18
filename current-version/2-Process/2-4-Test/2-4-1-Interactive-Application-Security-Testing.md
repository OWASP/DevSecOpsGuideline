# Interactive Application Security Testing

**IAST (interactive application security testing)** is an application security testing method that tests an application, API, or function while it is being exercised by automated tests, human testers, or any other "interaction" with the code's functionality. This makes it highly compatible with just about any software development lifecycle, especially DevOps.

IAST does not scan applications, but installs onto application and API servers and continuously analyzes applications forever. IAST works by instrumenting code with sensors that can directly observe security relevant application behavior. IAST uses the same proven technqiues as APM tools and profilers, just highly optimized for security and speed.

IAST requires zero changes to the way teams build, test, and deploy code. IAST performs security testing in real time during normal development and testing, and identifies vulnerabilities without requiring them to be exploited. This means with IAST, anyone can perform high quality security tests, even without a security background.

IAST can be deployed to development servers, CI/CD pipelines, or quality assurances servers, or even while in production. Wherever the code runs, that's where IAST is installed, including servers, containers, virtual machines, cloud, and other environments. IAST is uniquely well suited for API security testing, as it overcomes the challenges SAST and DAST have with complex API code and data.

IAST sensors have access to:
+ Entire code
+ Full HTTP request and response
+ Data flow and control
+ Configuration data
+ Libraries and frameworks and how they are used
+ Back-end connection data

This rich context makes IAST extremely accurate compared with traditional appsec testing tools and it enables IAST to deliver very detailed findings that enable developers to understand issues and fix them correctly. It also enables IAST to cover a very broad range of appsec vulnerabilities, including:
+ Code issues like hardcoded secrets and weak encryption algorithms
+ Data flow issues like injection and SSRF
+ HTTP issues like clickjacking, parameter pollution, and missing headers
+ Backend connection issues like SSRF
+ Configuration issues like verb tampering and weak authentication
+ and more...


One challenge with IAST is that only code that is exercised is tested. However, it's easy to use simple end-to-end "smoke" tests, or even a simple crawler, to generate this coverage. IAST does not require extensive functional testing, just basic end-to-end execution of routes.  Some IAST tools extract the set of routes from an application and simplify the process of getting to 100% route coverage.


---

## IAST vs SAST

**Static Application Security Testing** method examines source code in a non-runtime environment early in the SDLC. It looks for suspicious code patterns that indicate security risks. Even though they are easy to deploy, SASTs report large numbers of false positives because SASTs do not take into account the presence of other security countermeasures, and they lack visibility during runtime. SAST tools normally run during the build process, and can introduce delays as the scan process takes time to finish. IASTs are more flexible than SASTs, because they are applicable in production runtime environments (SASTs require direct access to the source code).

## IAST vs DAST

**Dynamic Application Security Testing** method works like a black-box scanner that sends malicious HTTP requests to an application and evaluate the HTTP responses to determine whether a security vulnerability was found. DASTs look at the applications from the exterior and determine the presence of risks by looking at the response (including body and headers) of the server to a battery of tests, but DASTs have no visibility of the internal workings of the app. Furthermore, DAST tests are hard to automate, because DASTs must be operated by experienced appsec teams, such as penetration testers, to be truly useful. Forrester estimates that the duration of a DAST scan can take around 5 to 7 days, while testing with IAST is a real-time (zero minutes) operation.

---

### Tools

+ [Contrast Assess](https://www.contrastsecurity.com/contrast-assess) and [Contrast Community Edition](https://www.contrastsecurity.com/contrast-community-edition)
+ [Checkmarx Interactive Application Security Testing(CxIAST)](https://www.checkmarx.com/products/interactive-application-security-testing/)
+ [Seeker Interactive Application Security Testing](https://www.synopsys.com/software-integrity/security-testing/interactive-application-security-testing.html)
+ [HCL AppScan on Cloud](https://cloud.appscan.com)

---
### References

+ [OWASP - Free IAST Tools](https://owasp.org/www-community/Free_for_Open_Source_Application_Security_Tools#:~:text=open%20source%20projects.-,IAST%20Tools,-IAST%20tools%20are)
+ [Contrast Security - What is Interactive Application Security Testing?](https://www.contrastsecurity.com/knowledge-hub/glossary/interactive-application-security-testing)
+ [Veracode - IAST](https://www.veracode.com/security/interactive-application-security-testing-iast)
+ [Hdivsecurity - IAST](https://hdivsecurity.com/bornsecure/what-is-iast-interactive-application-security-testing/)
+ [Synk - IAST](https://snyk.io/learn/iast-interactive-application-security-testing/)
+ [Acunetix - IAST](https://www.acunetix.com/blog/web-security-zone/what-is-iast-interactive-application-security-testing/)
+ [Contrast Security - Why the difference sast, dast, and iast mastters](https://www.contrastsecurity.com/security-influencers/why-the-difference-between-sast-dast-and-iast-matters)
+ [Esecurityplanet - Application security vendors](https://www.esecurityplanet.com/products/application-security-vendors/)
