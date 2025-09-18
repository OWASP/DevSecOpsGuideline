### Infrastructure as Code scanning

IaC scanning means checking the code used to set up and manage infrastructure. This code, written in tools like Terraform or Ansible, defines how servers, networks, and other parts of the infrastructure are created. The aim of IaC scanning is to find security problems and mistakes early on, before deploying the infrastructure. By doing this, teams can make sure that the infrastructure follows security rules and company policies right from the start. These checks happen as part of the development process before the code is used in live systems.

Let's consider a scenario where a development team is using Terraform to automate the provisioning of cloud resources in AWS. Here's a simplified example:

```terraform
# Terraform script to create an S3 bucket

provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "example_bucket" {
  bucket = "example-bucket"
  acl    = "public-read"
}
```

In this example, the Terraform script creates an S3 bucket named "example-bucket" with public read access (acl = "public-read").

During the IaC scanning process, a scanning tool might detect this configuration and flag it as a security risk because it allows public access to the bucket. This could potentially expose sensitive data stored in the bucket to unauthorized users.

As a result of the IaC scan findings, the development team might revise the Terraform script to ensure that the bucket is not publicly accessible.

In the next part, you will find a list of tools that can help you address different types of IaC scanning at various phases of your application development and deployment.

---

### Tools

- #### Infrastructure as Code Scanning Tools

  - [Checkov](https://github.com/bridgecrewio/checkov) - Prevent cloud misconfigurations during build-time for Terraform, Cloudformation, Kubernetes, Serverless framework and other infrastructure-as-code-languages with Checkov by Bridgecrew
  - [ansible-lint](https://github.com/ansible-community/ansible-lint) - Best practices checker for Ansible
  - [puppet-lint](https://github.com/rodjek/puppet-lint) - Check that your Puppet manifests conform to the style guide
  - [tfsec](https://github.com/tfsec/tfsec) - Security scanner for your Terraform code
  - [terrascan](https://github.com/accurics/terrascan) - Detect compliance and security violations across Infrastructure as Code to mitigate risk before provisioning cloud native infrastructure
  - [tflint](https://github.com/terraform-linters/tflint) - A Pluggable Terraform Linter
  - [Trivy](https://github.com/aquasecurity/trivy) - Provide built-in policies to detect configuration issues in Docker, Kubernetes, Terraform and CloudFormation. Also, you can write your own policies in Rego to scan JSON, YAML, etc, like Conftest.
  - [KICS](https://github.com/Checkmarx/kics) - Find security vulnerabilities, compliance issues, and infrastructure misconfigurations early in the development cycle of your infrastructure-as-code with KICS by Checkmarx.
