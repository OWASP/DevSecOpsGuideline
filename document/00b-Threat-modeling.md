## Threat Modeling 
Since an important part of the DevSecOps initiative is the threat modeling and evaluating the risk of them. So in this part, we want to take look into this topic.

### What is Threat Modeling? 
That is a systematically listing all the potential ways one can attack an application. So Threat Modeling is a process for looking at attacks actively. The output of this process is a list of threats or probable threat scenarios also our approach should be Holistic to consider all threats not a specific part of an application. On the other hand Threat modeling is a **Collaborative** and **Repeatable** process.  
#### Process Outputs:
+ Diagrams
+ Security requirements
+ Non-requirements
+ List of threats / vulnerabailties

#### Terms:
+ Weakness:  
A software defect or bug (Ex: missing user email validation)
+ Vulnerability:  
A weakness that can be exploited. (Ex: The user email field can be abused to insert SQL statement)
+ Attack
    - Target: the value of an attack
    - Attack Vector: the path that attacker can take to exploit a vulnerability
    - Threat Actor: threat source.
+ Attack Surface:  
Anything that can be obtained, used, or attacked by a threat actor
+ Risk:  
Risk = Impact * Likelihood

### Why Threat Modeling?
As main reasons for using threat modeling we can say: 
+ Pro-active approach to finding threats
+ Increasing efficiency by reducing cost 
+ A better prioritization based on bugs and mitigation plan 
+ A better understanding of the system

### Who should the threat model? 

+ Architect, who knows how the application has been designed and how data flows across. 
 + Developer, who knows the elaborate details on how the application was built, the detailed interactions between components.
+ Tester, who knows the requirements, and what the application is supposed to do. 
+ Security expert, who knows about specific attack factors and vulnerabilities.
However, the best answer to this question is, **It depends on the organization**.

### When to perform Threat modeling?
Since, the earlier you find vulnerabilities in software, the easier and cheaper it is to fix them, Threat Modeling should be as early as possible in the software design process. If you are working in an agile environment, ideally the threat modeling should be done during each sprint.

## Select the Right approach & Methodology
Here we have to term 1st is Approach that describes how one could start with the process with threat modeling and 2ns is Methodology which describes the process itself. So each of the methodologies is based on one of the 3 available approaches. 

### Approaches
+ **Asset-centric Approach**:  
According to the name, it turns around assets. So the producing steps are as follows:  
    1. Create a list of assets  
    2. Draw assets, components and data flows  
    3. For each element, check for threats   

By repeating these steps for all assets, a list of threats will be produced. 

+ **Attacker-centric Approach**:  
Staring threat modeling from an attacker perspective. So the producing steps are as follows:
    1. Create a list of threat actors
        - Motive
        - Means
        - Opportunity
    2. Create a list of threats

+ **Application-centric Approach**:
This one starts with visualizing the application instead of thinking about the risks or attacks first. So the producing steps are as follows:  
    1. Draw a diagram of the application  
    2. List threats for each element  
        - STRIDE  
        - OWASP TOP 10  
    
    3. Rank threats using a classification model

### Methodology

According to the approaches we have a list of methodology which are as follows:

+ [PASTA](https://blog.eccouncil.org/what-is-pasta-threat-modeling)
+ Microsoft Threat Modeling
+ [OCTAVE](https://blog.eccouncil.org/octave-threat-modeling-all-you-need-to-know)
+ [STRIDE](https://blog.eccouncil.org/what-is-stride-methodology-in-threat-modeling)
+ [TRIKE](https://blog.eccouncil.org/trike-threat-modeling-as-a-risk-management-tool)
+ VAST