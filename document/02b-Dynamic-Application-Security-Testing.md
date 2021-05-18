### Dynamic Application Security Testing (DAST)

DAST is a “Black-Box” testing, can find security vulnerabilities and weaknesses in a running application by injecting malicious payloads to identify potential flaws that allow for attacks like SQL injections or cross-site scripting (XSS), etc. DAST tools are especially helpful for detecting:
- Input or output validation
- Authentication issues
- Server configuration mistakes

DAST tools allow for sophisticated scans on the client side and server side without needing the source code or the framework the application is built on. They usually require minimal user interactions once configured and can be run as part of a nightly scan. As more important DAST tools we can look at the following:  
- Dynamic security scanner 
- Fuzzers
- Attack Proxies

---
### Tools
- #### Open-source:
  + [ZED Attack Proxy](https://www.zaproxy.org) - It is an open source tool which is offered by OWASP for performing security testing

- #### Commercial:
  + [Acunetix](https://www.acunetix.com) - An automatic web security testing scanner that accurately scans and audits all web applications, including HTML5, JavaScript and Single Page applications (SPAs)
  + [Netsparker](https://www.netsparker.com) - It can identify vulnerabilities in all types of modern web applications, regardless of the underlying architecture or platform
  + [InsightAppSec (AppSpider)](https://www.rapid7.com/products/insightappsec) - Application security testing for the modern web
  + [Veracode Dynamic Analysis](https://www.veracode.com/products/dynamic-analysis-dast) - Veracode Dynamic Analysis helps companies scan their web applications for exploitable vulnerabilities at scale
  + [Burp Suite](http://www.portswigger.net/) is an integrated platform for performing security testing of web applications. Its various tools work seamlessly together to support the entire testing process, from initial mapping and analysis of an application’s attack surface, through to finding and exploiting security vulnerabilities.

---
### References
+ [OWASP - Vulnerability Scanning Tools](https://owasp.org/www-community/Vulnerability_Scanning_Tools)
+ [RAPID7 - Dynamic Application Security Testing](https://www.rapid7.com/fundamentals/dast/)