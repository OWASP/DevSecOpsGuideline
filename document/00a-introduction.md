## An introduction about DevSecOps
Today, DevOps is empowering any organizations to deploy changes to production environments at blazing rates. Since time to deliver is so important feature during this process, The main question for a security person is, How I can secure this process? or how much our deliverable products are secure?
In this regard, we can embed some security-related steps entire our DevOps process to perform some automated tests. So considering the DevSecOps or secure DevOps culture helps us to promote the shift-left security strategy in our company, At least in the tech department. 
### What's the Shift-left security strategy? 
As a simple definition, The shift-left security strategy is a way or solution to embedding security as a part of our development process and consider security from the inception steps of application or system design. In other words, security is responsible for everyone who works in the software development and operating process. 
Of course, security is a profession and we need highly skilled people to play security-related roles but in this approach, any designer, software architecture, developer, DevOps engineer, and ...  together with security guys have liability about security. 

### Dev+Sec+Ops
<img align="right" width="200" height="180" src="/document/assets/images/DevSecOps.png">

Suppose that these 3 deferent areas for covering each other is something like the image, So in conclusion with the above words, we need to implement some tools and working on promoting a DevSecOps culture too. 

As Shannon Lietz said:
> "The purpose and intent of DevSecOps is to build on the mindset that "everyone is responsible for security" with the goal of safely distributing security decisions at speed and scale to those who hold the highest level of context without sacrificing the safety required."

### The DevSecOps culture:
As you heard before we want to talk about the Shift-left security. It means we should consider security from design (in a simple definition) which target is moving security sooner in the development process. 
Let me a bit explain it, suppose that you are working in a DevOps based team and you are traditionally doing security test (Yes, end of all QA tests and before going to production), What's Happen? 
Well, all bugs should be fixed ASAP, Developer team is under pressure to fix issues, QA tests should be performed again, and security test again. this means the cost will be increased, money and time. In the end, you sacrifice agility for security things do not like a business team. But what is the solution? 

The solution is embedding security in the process and did not put it as a final step. Considering security in design by threat modeling and break down huge security tests to smaller security testing and put as parts of the development pipeline. 

In the following picture you can see differences between DevOps and DevSecOps cycle. 
<img src="/document/assets/images/DevOps vs DevSecOps.png">


### Testing
When, we are talking about testing we should have in mind we have different definitions in testing which is can change our route to atchiving a secure DevSecOps cycle. Let's take look into this defenitions. 
#### Different test paths
1. **Positive testing**  
Positive testing is a kind of software testing that is performed by assuming everything will be as expected. It is performed with the assumption that only valid and relevant things will happen. data set and all other functionalities will be as expected.
2. **Negative testing**  
Negative testing is a type of software testing that is performed to check the system for unexpected conditions. Negative testing plays a much important role in high-performance software development. It checks whether on such unexpected conditions what will be the behavior of the software.

#### Methods of testing
1. **Static testing**  
Static Testing is a type of a Software Testing method which is performed to check the defects in software without actually executing the code of the software application. Static testing is performed in early stage of development to avoid errors as it is easier to find sources of failures and it can be fixed easily. The errors that can’t not be found using Dynamic Testing, can be easily found by Static Testing.
2. **Dynamic testing**  
 Dynamic Testing is a type of Software Testing which is performed to analyze the dynamic behavior of the code. It includes the testing of the software for the input values and output values that are analyzed.

----
#### Refrences
1. https://www.geeksforgeeks.org/difference-between-positive-testing-and-negative-testing/
2. https://www.geeksforgeeks.org/difference-between-static-and-dynamic-testing/
