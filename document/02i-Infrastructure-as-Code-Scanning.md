### Infrastructure as Code (IaC) Scanning

IaC also known as software-defined infrastructure, allows the configuration and deployment of infrastructure components faster with consistency by allowing them to be defined as a code and also enables repeatable deployments across environments.

IaC Scanning, analyzes code in isolation, identifying risks, misconfigurations, and compliance faults only relevant to the IaC itself. IaC scanning tools can parse common cloud-native template formats. They can then apply rules based on security best practices, providing users with an understanding of where additional hardening may be required to enhance the security of their environments.

These tools can isolate issues such as a Kubernetes manifest that requests privileged access to the file system of a node, a Docker image created to run as the root user, or a Terraform script that configures an S3 bucket, which is accessible worldwide.

You can use IaC scanning tools at various stages in the development process, by IT professionals as a component of a CI/CD pipeline in a test suite, or as an element of the initial authoring. 
