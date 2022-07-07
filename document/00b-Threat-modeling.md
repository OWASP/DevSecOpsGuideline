## Threat Modeling
An important part of the DevSecOps initiative is Threat Modeling. Threat Modeling is a structured activity of risk identification and management. So in this part, we want to take look more into this topic.

### What is Threat Modeling?
This is a process of listing all the potential ways in which one can attack your application. The output of the process is a list of threat scenarios together with their mitigations.

Our approach should be holistic to cover all threats. To realize this, we should not focus only on a specific part of an application.

Another important note is that Threat Modeling is a **Collaborative** and **Repeatable** process.

#### Process Outputs:
+ Diagrams
+ Security requirements
+ Non-requirements
+ List of threats / vulnerabilities and its mitigation

#### Terms:
+ Weakness
  - A software defect or bug. (Ex: missing user email validation)
+ Vulnerability
  - A weakness that can be exploited. (Ex: we can abuse the user email field to insert SQL statements)
+ Attack
    - Target: the value of an attack
    - Attack Vector: the path that the attacker can take to exploit a vulnerability
    - Threat Actor: threat source.
+ Attack Surface
  - Anything that can be obtained, used, or attacked by a threat actor.
+ Risk
  - Risk = Impact * Likelihood
  - Impact: Size of negative consequences that each risk brings.
  - Likelihood: Probability of a risk to happen.
+ Approach
  - Describes how one could start with the process.
+ Methodology
  - Describes the process itself.

### Why Threat Modeling?
As the main reasons for using threat modeling, we can say:
+ Pro-active approach to finding threats
+ Increasing efficiency by reducing cost
+ A better prioritization based on bugs and a mitigation plan
+ A better understanding of the system


### Who should be involved in the threat modeling?
+ Architect - knows how the application has been designed and how data flows across.
 + Developer - knows how the application was built, and the interactions between components.
+ Tester - knows the requirements, and what the application is supposed to do.
+ Security expert - knows about specific attack factors and vulnerabilities.

But, the best answer to this question is, **it depends on the organization**.

### When to perform Threat modeling?
Ideally, Threat Modeling should be performed early in the software design process. This allows for easier and cheaper fixes.

In an Agile environment, Threat Modeling should be done during each sprint. But, we do not have to start from scratch each time. Each sprint only requires an iteration of the previous threat model output.

## Selecting the Right Approach & Methodology
### Methodology
Common Threat Modeling methodologies are:
+ PASTA
+ Microsoft Threat Modeling
+ OCTAVE
+ TRIKE
+ VAST

Each of the available methodologies listed above are based on one of the 3 common approaches:

### Approaches
#### **Asset-centric Approach**
  - Steps:
    1. Create a list of assets
    2. Draw assets, components, and data flows
    3. For each element, check for threats

#### **Attacker-centric Approach**
  - Steps:
    1. Create a list of threat actors
        - Motive
        - Means
        - Opportunity
    2. Create a list of threats

#### **Application-centric Approach**
  - Steps:
    1. Draw a diagram of the application
    2. List threats for each element
        - STRIDE
        - OWASP TOP 10
    3. Rank threats using a classification model
