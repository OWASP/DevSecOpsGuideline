## Introduction to the OWASP DevSecOps Guideline  
The OWASP DevSecOps Guideline explains how we can transition from a traditional approach to achieving security that starts with requirements and ends with security testing to an approach that brings together Development, Security, and Operations throughout the software lifecycle -- a "DevSecOps" approach.

This project's goal is to help companies of any size to add security to their DevOps pipeline and culture. There is no one **right** way to do DevSecOps, so it's important to stay focused.  

DevSecOps strives to **"produce demonstrably secure code"** by:
* leveraging automation to create short feedback loops to developers
* breaking down the silos between development, security, and operations
* breaking down security work into small pieces to create flow
* making decisions based on threat intelligence from operations
* establishing a culture of security experimentation and learning

There are tools to support security processes across the software development lifecycle. Every company should have processes in place to ensure:
* **Custom Code Security** - your custom code has the right defenses and is free from vulnerabilities, including applications, APIs, serverless, mobile, infrastructure as code, etc...
* **Supply Chain Security** - your platform, framework, libraries, containers, and other components 
* **Runtime Protection** - you detect attacks on your software and prevent them from being exploited 

If you do these three processes well, you will be in relatively good shape in terms of application security. In this document, we will explore a variety of automated solutions that can help you implement these three processes.

The goal is not to use all of the tools in your pipeline.  The goal is to ensure secure code emerges from your pipeline. You need to pick and choose the tools that are effective with your organization's people, process, technology, and culture. You will very likely want to use each tool for what it is best at, rather than repeating all tests with all tools.  Of course, every software development organization is different and you are free to select tools and the exact location where you want to implement the tools. 

![Secure Pipeline](/document/assets/images/Pipeline-view.png)