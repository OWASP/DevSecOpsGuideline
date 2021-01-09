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
### TOOLS
- #### Tools (Static Code Analysis):
  + **SonarQube** It is an open-source web-based tool, extending its coverage to more than 20 languages, and also allows a number of plugins. [HomePage](https://www.sonarqube.org/)
  + **Veracode** Veracode is a static analysis tool that is built on the SaaS model. This tool is mainly used to analyze the code from a security point of view. [HomePage](https://www.veracode.com/security/static-analysis-tool)


- #### Tools (IaC scanning): 
  + **Checkov** Prevent cloud misconfigurations during build-time for Terraform, Cloudformation, Kubernetes, Serverless framework and other infrastructure-as-code-languages with Checkov by Bridgecrew. [GitRepo](https://github.com/bridgecrewio/checkov)
  + **ansible-lint** Best practices checker for Ansible. [GitRepo](https://github.com/ansible-community/ansible-lint)
  + **puppet-lint** Check that your Puppet manifests conform to the style guide. [GitRepo](https://github.com/rodjek/puppet-lint)
  + **tfsec** Security scanner for your Terraform code. [GitRepo](https://github.com/tfsec/tfsec)
  + **terrascan**  Detect compliance and security violations across Infrastructure as Code to mitigate risk before provisioning cloud native infrastructure. . [GitRepo](https://github.com/accurics/terrascan)
  + **tflint**  A Pluggable Terraform Linter. [GitRepo](https://github.com/terraform-linters/tflint)

  
  
- #### Tools (Dependency scanning): 
  + **OWASP Dependency-check** Dependency-Check is a Software Composition Analysis (SCA) tool that attempts to detect publicly disclosed vulnerabilities contained within a project’s dependencies. It supports Java, .NET, JavaScript, and Ruby. [Home Page](https://owasp.org/www-project-dependency-check/)
  + **RetireJS** RetireJS is an open-source, JavaScript-specific dependency checker. [GitRepo](https://github.com/RetireJS/retire.js)
  + **Hakiri** Hakiri is a commercial tool that offers dependency checking for Ruby and Rails-based GitHub projects using static code analysis. [HomePage](https://hakiri.io/)
