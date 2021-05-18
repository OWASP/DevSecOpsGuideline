### Static scanning is an important part of the proces!
<img align="right" width="360" height="200" src="/document/assets/images/Static scanning.png">
Static Code Analysis or Source Code Analysis is usually part of a Code Review (white-box testing) and it is a method of computer program debugging that is done by examining the code without executing the program.</br>
Static scanning is good way finding coding issues such as:

+ Syntax violations
+ Security vulnerabilities
+ Programming errors
+ Coding standard violations
+ Undefined values

For more information about the Static Code Analysis please visit [the OWASP page](https://owasp.org/www-community/controls/Static_Code_Analysis)
To achieve a better result we can combine static security scanning and 3rd party code (open-source libraries (dependency)) scanning.
To doing this part better and more complete (prevent misconfigurations), here we can bring up IaC (Infrastructure as code) security scan too. For example check Terraform, helm, Ansible code, etc.  
So according to the above lines the possible actions in this step are as follows:
+ Static Code Analysis
+ open-source libraries (3rd party / dependency) scanning
+ IaC Security scanning

---
### Tools
- #### Static Code Analysis:
  + [SonarQube](https://www.sonarqube.org) - An open-source web-based tool, extending its coverage to more than 20 languages, and also allows a number of plugins
  + [Veracode](https://www.veracode.com/security/static-analysis-tool) - A static analysis tool that is built on the SaaS model. This tool is mainly used to analyze the code from a security point of view
  + [security code scan](https://github.com/security-code-scan/security-code-scan) - Vulnerability Patterns Detector for C# and VB.NET
  + [Brakeman](https://github.com/presidentbeef/brakeman) - A static analysis security vulnerability scanner for Ruby on Rails applications
  + [Enlightn](https://github.com/enlightn/enlightn) - A static analysis vulnerability scanner for Laravel PHP applications
  + [Inquisition](https://github.com/rubygarage/inquisition) - A set of tools for convenient technical analysis of web applications built with Ruby and Ruby on Rails. Now you don't need to set up and configure every single gem. Use Inquisition gem instead

- #### IaC scanning: 
  + [Checkov](https://github.com/bridgecrewio/checkov) - Prevent cloud misconfigurations during build-time for Terraform, Cloudformation, Kubernetes, Serverless framework and other infrastructure-as-code-languages with Checkov by Bridgecrew
  + [ansible-lint](https://github.com/ansible-community/ansible-lint) - Best practices checker for Ansible
  + [puppet-lint](https://github.com/rodjek/puppet-lint) - Check that your Puppet manifests conform to the style guide
  + [tfsec](https://github.com/tfsec/tfsec) - Security scanner for your Terraform code
  + [terrascan](https://github.com/accurics/terrascan) - Detect compliance and security violations across Infrastructure as Code to mitigate risk before provisioning cloud native infrastructure
  + [tflint](https://github.com/terraform-linters/tflint) - A Pluggable Terraform Linter