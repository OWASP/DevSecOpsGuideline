## What is Policy
In each company there are lots of rules, requirements, or procedures that must consider before deploying any application or product to be in production level, and other of them for other type of level like staging or developing. These rules, requirements, or procedures must check and pass and if there is any misconfiguration, process has to be suspend until it fix.

Some must comply with industry-recognized frameworks such as SOC 2, CIS, PCI DSS, or ISO 27001. These policies are either part of the business logic code or enforced manually.These are not easily trackable because every team implements it as it sees fit due to a lack of framework definition in organization level.

## What is Policy as Code
Having multiple security checklist in your organization will come to be time consuming and makes lots of differents meaning and behaviour in each team. despite of having a checklist or excel, you can manage all policies as code and make all of them proactive and apply them in each enviroment you need them. by this approach policeis are not only a checklist that one team can ignore some part of it or miss any part of it.

## Benefits of Policy as Code
**Policy Management**: Centralizing your policies into a single location, as opposed to dispersing them across multiple locations maintained by different IT teams, enables a more agile and adaptable approach to policy management.

**Version Control**: Centralizing policies in a version control system like GitHub or GitLab offers organizations enhanced control and visibility. Stakeholders benefit from easy access to operational changes, while automated version control facilitates seamless updates and rollback options, ensuring smooth transitions and mitigating potential issues with new versions.

**Faster and Efficient**: Efficiency is heightened as manual policy enforcement is eliminated, enabling dynamic updates and sharing of policies, thereby streamlining the process. Additionally, the combination of centralization and versioning fosters repeatability and idempotence in code execution. Repeatability ensures consistent code execution, while idempotence guarantees that repeated executions yield the same output. This reliability is crucial for instilling confidence among operators, empowering them to execute deployments without hesitation or fear.

### Tools
- #### Open-source:
  + [OPA](https://www.openpolicyagent.org/) - Open Policy Agent (OPA) is an open source, general-purpose policy engine that enables unified, context-aware policy enforcement across the entire stack.
  + [Kyverno](https://kyverno.io/) - Kyverno (Greek for “govern”) is a policy engine designed specifically for Kubernetes.

- #### Commercial:
  + [Styra DAS](https://www.styra.com/pricing/) - Commercial tools for managing OPA at scale and created by the founders and maintainers of Open Policy Agent (OPA)
  + [HashiCorp Sentinel](https://developer.hashicorp.com/sentinel) - A language and framework for policy built to be embedded in existing software to enable fine-grained, logic-based policy decisions.
