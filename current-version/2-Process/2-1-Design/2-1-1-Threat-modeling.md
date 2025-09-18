## Threat Modeling
Threat modeling is a crucial component of the DevSecOps approach, focused on identifying and managing risks in a structured way. Here’s a more detailed look at this topic:

### What is Threat Modeling?
Threat modeling involves enumerating all potential attack vectors on an application, producing a list of threat scenarios along with mitigations. This holistic and collaborative process ensures comprehensive coverage of potential threats.

Another important note is that Threat Modeling is a **Collaborative** and **Repeatable** process and it is a process **NOT** a project!

#### Key Outputs:
+ **System Diagrams:** Detailed representations of the architecture and data flows.
+ **Security Requirements:** Specific criteria for safeguarding the system.
+ **Threat List:** Catalog of potential threats with mitigation strategies.

#### Terms:
+ **Weakness:** A software defect or bug. (e.g., input validation errors,  missing user email validation)
+ **Vulnerability:** A weakness that can be exploited. (Ex: we can abuse the user email field to insert SQL statements)
+ **Attack:** Exploitation of vulnerabilities.
    - **Target:** The objective of the attack (e.g., sensitive data).
    - **Attack Vector:** The path that the attacker can take to exploit a vulnerability (e.g., web interface).
    - **Threat Actor:** The threat source (e.g., hacker, insider).
+ **Attack Surface:** Anything that can be obtained, used, or attacked by a threat actor.
+ **Risk:** Impact and likelihood of a threat being exploited (Risk = Impact x Likelihood).
  - **Impact:** Size of negative consequences that each risk brings.
  - **Likelihood:** Probability of a risk to happen.
+ **Approach:** Describes how one could start with the process.
+ **Methodology:** Describes the process itself.

### Why Threat Modeling?
As benefits ofthreat modeling, we can say:
+ **Proactive Threat Identification:** Early discovery of potential security issues.
+ **Cost Efficiency:** Mitigating threats early reduces remediation costs.
+ **Prioritization:** Focus on the most critical vulnerabilities.
+ **System Understanding:** Better comprehension of system interactions and data flows.


### Who should be involved in the threat modeling?
+ **Architect:** Knows how the application has been designed and how data flows across to ensure proper design and flow.
+ **Developer:** Knows how the application was built, and the interactions between components to provide insight into code and interactions.
+ **Tester:** Knows the requirements, and what the application is supposed to do, to validate requirements and behavior.
+ **Security expert:** Knows about specific attack factors and vulnerabilities to identify and assess security risks.

But, the best answer to this question is, **it depends on the organization**.

### When to perform Threat modeling?
Ideally, Threat Modeling should be performed early in the software design process. This allows for easier and cheaper fixes.

In an Agile environment, Threat Modeling should be done during each sprint. But, we do not have to start from scratch each time. Each sprint only requires an iteration of the previous threat model output.

## Selecting the Right Approach & Methodology
### Common Methodologies
Common Threat Modeling methodologies are:
+ **PASTA (Process for Attack Simulation and Threat Analysis):** Focuses on business impact.
+ **Microsoft Threat Modeling:** Uses data flow diagrams (DFDs) to identify threats.
+ **OCTAVE (Operationally Critical Threat, Asset, and Vulnerability Evaluation):** Emphasizes organizational risk.
+ **TRIKE:** A security auditing framework.
+ **VAST (Visual, Agile, and Simple Threat):** Supports Agile development with automation.


### Approaches
| **Approach**            | **Steps**                                                                                                                                                                   |
|-------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| **Asset-Centric**       | 1. Identify and classify assets. <br> 2. Diagram components and data flows. <br> 3. Identify threats specific to each element.                                              |
| **Attacker-Centric**    | 1. Define potential threat actors (e.g., insiders, external hackers). <br> 2. Determine their motives, means, and opportunities. <br> 3. List and prioritize potential threats. |
| **Application-Centric** | 1. Create detailed diagrams of the application. <br> 2. Identify threats for each element. <br> 3. Use threat classification models (e.g., STRIDE, OWASP Top 10). <br> 4. Rank threats using risk classification models (e.g., DREAD - Damage, Reproducibility, Exploitability, Affected Users, Discoverability). |

### Detailed Steps for Each Approach
#### Asset-Centric
1. Asset Identification:
    - List all assets, including data, software, and hardware.
    - Classify assets based on their criticality and sensitivity.
2. Component Diagramming:
    - Use data flow diagrams (DFDs) to map out interactions.
    - Highlight trust boundaries and data entry points.
3. Threat Identification:
    - Analyze each component for possible threats.
    - Use tools like Microsoft Threat Modeling Tool to automate threat discovery.
4. Threat Mitigation:
    - Develop specific countermeasures for each identified threat.
    - Prioritize mitigations based on risk assessment.

#### Attacker-Centric
1. Threat Actor Identification:
    - Identify potential attackers (e.g., external hackers, malicious insiders).
    - Categorize actors by their access level and intent.
2. Attacker Profiling:
    - Understand attackers’ goals and capabilities.
    - Use threat intelligence sources to gather information about typical attack methods.
3. Threat Enumeration:
    - List potential attack scenarios.
    - Use attack trees to map out how an attacker might exploit vulnerabilities.
4. Threat Mitigation:
    - Implement defenses like intrusion detection systems, access controls, and encryption.
    - Regularly update threat profiles and defenses based on new intelligence.

#### Application-Centric
1. Application Diagramming:
    - Create detailed architecture diagrams.
    - Include data flows, components, and interactions.
2. Threat Identification:
    - Apply models like STRIDE or OWASP Top 10 to each component.
    - Identify threats such as spoofing, tampering, and data breaches.
3. Risk Assessment:
    - Use the DREAD model to evaluate threats.
    - Rank threats based on their potential impact and exploitability.
4. Threat Mitigation:
    - Develop countermeasures for high-risk threats.
    - Implement secure coding practices and conduct regular security reviews.


### What is DREAD?
DREAD is a risk assessment model used in cybersecurity to evaluate and prioritize potential threats. The acronym stands for:
  - **Damage potential:** Assessing the potential damage that could result from a successful exploit.
  - **Reproducibility:** Evaluating how easily the exploit can be replicated.
  - **Exploitability:** Determining the ease with which the vulnerability can be exploited.
  - **Affected users:** Identifying the number of users or systems affected by the vulnerability.
  - **Discoverability:** Assessing how easily the vulnerability can be discovered.

Each of these factors is typically scored on a scale, often from 0 to 10, with higher scores indicating a greater level of risk.


## Practical Steps for Threat Modeling:
  1. **Define Scope:** Identify boundaries of the system and critical assets.
  2. **Create Diagrams:** Develop DFDs and architecture diagrams.
  3. **Identify Threats:** Use methodologies like STRIDE to discover potential threats.
  4. **Analyze Threats:** Assess risk using models like DREAD.
  5. **Develop Mitigations:** Define strategies to mitigate identified threats.
  6. **Review and Iterate:** Regularly update the threat model throughout the development lifecycle.


---
## Tools:
- #### Open-source:
+ [OWASP Threat Dragon](https://owasp.org/www-project-threat-dragon/) - An open-source tool for creating threat model diagrams and managing threats.
+ [Microsoft Threat Modeling Tool](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool) - A tool for creating data flow diagrams and identifying threats using STRIDE.
+ [CAIRIS](https://cairis.org/): A tool for building models and conducting risk assessments based on these models.
+ [threat-composer](https://github.com/awslabs/threat-composer?tab=readme-ov-file) - A simple threat modeling tool to help humans to reduce time-to-value when threat modeling.

- #### Commercial:
+ [ThreatModeler](https://threatmodeler.com/) - An enterprise-grade tool for automated threat modeling, integrating with CI/CD pipelines.
+ [IriusRisk](https://www.iriusrisk.com/threat-modeling-platform) - A platform for automated threat modeling and risk management.

---
### Links:
- [OWASP - Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Awesome Threat Modeling](https://github.com/hysnsec/awesome-threat-modelling)
- [Threat Modeling Cheat Sheet](https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Threat_Modeling_Cheat_Sheet.md)
