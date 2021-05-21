## DevSecOps Intro

Today, DevOps is empowering any organizations to deploy changes to production environments at blazing rates.
Since time to deliver is so important feature during this process, the main question for a security person is
"How I can secure this process?" or "How much our deliverable products are secure?".
In this regard, we can embed some security-related steps entire our DevOps process to perform some automated tests.
So considering the DevSecOps or secure DevOps culture helps us to promote the shift-left security strategy in our company,
at least in the tech department.

### What's the Shift-left security strategy?

As a simple definition, the shift-left security strategy is a way or solution to embedding security as a part of our development process
and consider security from the inception steps of application or system design.
In other words, security is responsible for everyone who works in the software development and operating process.
Of course, security is a profession and we need highly skilled people to play security-related roles;
but in this approach, any designer, software architecture, developer, DevOps engineer, and ... together with security guys have liability about security.

### Dev+Sec+Ops

<img align="right" width="200" height="180" src="/document/assets/images/DevSecOps.png">

Suppose that these 3 different areas for covering each other is something like the image,
so in conclusion with the above words, we need to implement some tools and working on promoting a DevSecOps culture too.

As Shannon Lietz - founder at DevSecOps foundation - said:

> The purpose and intent of DevSecOps is to build on the mindset that
> "everyone is responsible for security" with the goal of safely distributing
> security decisions at speed and scale to those who hold the highest level of
> context without sacrificing the safety required."

### The DevSecOps culture

As you heard before we want to talk about the Shift-left security.
It means we should consider security from design (in a simple definition) which target is moving security earlier in the development process.

Let's suppose that you are working in a DevOps team and you are traditionally doing security test
(yes, end of all QA tests and before going to production), what happens?
Well, all bugs should be fixed ASAP, Developer team is under pressure to fix issues,
QA tests should be performed again, and security test again.
This means that the costs, money and time, increase.
In the end, you sacrifice agility for security things do not like a business team.

The solution is introducing security earlier in the process instead of having it in the final steps.
Considering security in design by threat modeling and
break down huge security tests in smaller security testing and integrating them in the development pipeline.

The following picture shows the differences between DevOps and DevSecOps lifecycles.
<img src="/document/assets/images/DevOps vs DevSecOps.png">

### Privacy

Privacy has become a major topic for companies of all sizes, since GDPR (Europe’s General Data Protection Regulations), CCPA (California Consumer Privacy Act), LGPD – Brazil’s Lei Geral de Proteção de Dados, and other laws and regulations are being enforced around the world.

Applications that will process a large volume of PII (personally identifiable information) should adapt the DevSecOps to follow the Privacy by Design approach, where the development process addresses privacy concerns thru the whole cycle.

### Software testing strategies

When, we talk about testing we should have in mind
we have different definitions in testing which is can change our route to achieving
a secure DevSecOps cycle.
Let's take look into this definitions.

#### Different software testing strategies

1. **Positive testing**

Positive testing assumes that, under normal conditions and inputs,
everything will behave as expected.
It is performed with the assumption that only valid and relevant things will happen:
data set and all other functionalities will be as expected.

2. **Negative testing**

Negative testing checks the system behavior under unexpected conditions.
Negative testing plays a much important role in high-performance software development:
it checks the software behavior under unexpected conditions and inputs.

#### Methods of testing

1. **Static testing**

   Static Testing checks software defects without executing the application code.
   It is performed in the early stage of development to avoid errors, as it is easier to find sources of failures and it can be fixed easily.
   Some issues that can’t be found using Dynamic Testing, can be easily found by Static Testing. Such issues consists of hard coded credentials, deprecated encryption algorithms, 2nd order injections, weak random, etc. 
   Most static analysis tools have the testing scope limited to one component and can not perform tests across different components. (EG. for a microservice architecture, static analysis tools will test each microservice independently)
   ![Static testing](/document/assets/images/sast_scanning.png)


2. **Dynamic testing**

   Dynamic Testing analyzes the behavior of the application code at runtime. Scanners send specially crafted requests to the target application. Request parameters are constantly modified during testing to try and expose a range of vulnerabilities. Based on the response of the application the tool can then identify potential vulnerabilities and report back. Some issues that can't be found by static analysis are easily detected by dynamic analysis. Such issues include client side vulnerabilities like authentication & session issues, sensitive data sent in plain text, etc. 
   Dynamic analysis tools have the posibility of testing the entire application flow(multiple components at once). (Eg. for a microservice architecture, dynamic analysis tools can point to one microservice, but as they interact with eachother results will represent the behaviour of the entire application)
   ![Dynamic testing](/document/assets/images/dast_scanning.png)
   

3. **Interactive analysis**
   
   Also known as Interactive Application Security Testig (IAST) monitors the application while other systems interact with it and observe vulnerabilities. This is achieved via sensors or agents deploy with the application. The sensors can see the entire flow from HTTP request down to the executed code, tracing the data through the application. Similar to static analysis, it can test one component at a time, but not multiple components. However, if agents/sensors are deployed on all components, when they interact with eachother this could reveal vulnerabilities in each component used in the application. (Eg. for a microservice architecture, only the microservices that have agents/sensors attached will report vulnerabilities)
   ![Interactive analysis](/document/assets/images/iast_analysis.png)

---

#### References

1. https://www.geeksforgeeks.org/difference-between-positive-testing-and-negative-testing
2. https://www.geeksforgeeks.org/difference-between-static-and-dynamic-testing
