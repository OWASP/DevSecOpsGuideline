# Static scanning is an important part of the process

![Static scanning diagram showing analysis process](/current-version/assets/images/Static scanning.png)

Static Code Analysis or Source Code Analysis is usually part of a Code Review (white-box testing) and it is a method of computer program debugging that is done by examining the code without executing the program.

Static scanning is good way finding coding issues such as:

- Syntax violations
- Security vulnerabilities
- Programming errors
- Coding standard violations
- Undefined values

For more information about the Static Code Analysis please visit [the OWASP page](https://owasp.org/www-community/controls/Static_Code_Analysis)
To achieve a better result we can combine static security scanning and 3rd party code (open-source libraries (dependency) scanning.
To doing this part better and more complete (prevent misconfigurations), we can bring up IaC (Infrastructure as code) security scan too. For example check Terraform, helm, Ansible code, etc.
So according to the above lines the possible actions in this step are as follows:

- Static Code Analysis (known as SAST)
- Open-source libraries (3rd party / dependency) scanning (known as SCA)
- IaC Security scanning

---

## Tools[^1]

### Open-source

- [Brakeman](https://github.com/presidentbeef/brakeman) - A static analysis security vulnerability scanner for Ruby on Rails applications
- [CodeQL](https://github.com/github/codeql) - Discover vulnerabilities across a codebase with CodeQL, our industry-leading semantic code analysis engine.
- [CodeSec by Contrast Security](https://www.contrastsecurity.com/developer) - A high-speed high-quality free SAST tool designed for use by developers and in CI/CD pipelines.
- [SonarQube](https://www.sonarqube.org) - An open-source web-based tool, extending its coverage to more than 20 languages, and also allows a number of plugins

### Commercial

- [Checkmarx SAST](https://checkmarx.com) - A static analysis security vulnerability scanner
- [CodeSweep](https://hclsw.co/codesweepgithub) - Static Analysis tool for GitHub that's free to use and can scan code on pull request. Support over 20 languages and IaC (docker, k8s). VS Code version can be found [here]( https://hclsw.co/codesweep)
- [Enlightn](https://github.com/enlightn/enlightn) - A static analysis vulnerability scanner for Laravel PHP applications
- [Fortify](https://www.microfocus.com/en-us/cyberres/application-security/static-code-analyzer) - A static analysis security vulnerability scanner
- [HCL AppScan on Cloud](https://cloud.appscan.com ) - SAST tool built as a service. The tool can perform traditional SAST, SCA and IaC scanning.
- [Inquisition](https://github.com/rubygarage/inquisition) - A set of tools for convenient technical analysis of web applications built with Ruby and Ruby on Rails. Now you don't need to set up and configure every single gem. Use Inquisition gem instead
- [PT Application Inspector](https://www.ptsecurity.com/ww-en/products/ai/) - Is the only source code analyzer providing high-quality analysis and convenient tools to automatically confirm vulnerabilities — significantly speeding up the work with reports and simplifying teamwork between security specialists and developers
- [security code scan](https://github.com/security-code-scan/security-code-scan) - Vulnerability Patterns Detector for C# and VB.NET
- [Semgrep](https://semgrep.dev) - Lightweight static analysis for many languages. Find bug variants with patterns that look like source code.
- [Veracode](https://www.veracode.com/security/static-analysis-tool) - A static analysis tool that is built on the SaaS model. This tool is mainly used to analyze the code from a security point of view

---

### Links

[^1]: Listed in alphabetical order.
