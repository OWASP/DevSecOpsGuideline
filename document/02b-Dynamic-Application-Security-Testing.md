### Dynamic Application Security Testing (DAST)

DAST is a “Black-Box” testing technique that can find security vulnerabilities and weaknesses in a running application by injecting malicious payloads to identify potential flaws that allow for attacks like SQL injections or cross-site scripting (XSS), etc. DAST tools are especially helpful for detecting:
- Input or output validation
- Authentication issues
- Server configuration mistakes

DAST tools allow for extensive scans from the client side and server side without needing the source code or the framework the application is built on. While configuration requires expertise, scans usually require minimal user interaction once configured and can be run as part of a nightly scan. As more important DAST tools we can look at the following:  
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
  + [HCL AppScan on Cloud](https://cloud.appscan.com) - DAST tool built as a service. It can scan both public and privatly hosted application. Can explore and test modern web applications, leverage manually recorded steps and handle complex login scenarios. 
  + [Nuclei](https://github.com/projectdiscovery/nuclei) - Fast and customisable vulnerability scanner based on simple YAML based DSL.

---
### References

+ [OWASP - Vulnerability Scanning Tools](https://owasp.org/www-community/Vulnerability_Scanning_Tools)
+ [RAPID7 - Dynamic Application Security Testing](https://www.rapid7.com/fundamentals/dast/)
