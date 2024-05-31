## Container Vulnerability Scanning
As containers become an almost ubiquitous method of packaging and deploying applications, the instances of malware have increased. Securing containers is now a top priority for DevOps engineers. Fortunately, a number of open source programs are available that scan containers and container images. Let’s look at five such tools.

### What can Container Security Scanning do?
- Detect insecure containers
    + Detect outdated libraries
    + Detect incorrectly configured containers
    + Detect outdated operating system
- Detect compliance validations
- Suggest best practices

### Issues with Container Security Scanner
- Level of depth depends on tool being used, So the results that you'll get are very dependent on the type of tool you choose.
- Easy to go "too far" with configuration, there are tools where you can configure so much different settings, that it's easy to jump overboard.
- The scan results will lead to actionable events?

### Where and When to use Container Scanner? 
<img align="center" src="/documents/assets/images/Dev-process.png">  

You can use it at the build phase when you're actually building for instance a Dockerfile and looking at the resulting image that you're creating. Another location to perform container scanning would be when you push a container to the registry or when you pull a container from a registry. However, a good approach is scanning before pushing into a trusted container registry then you can say we have a container registry with a scanned version of all images and for deploying in production you can pull from this trusted container registry. (Plase take look into the following image)

<img align="center" src="/documents/assets/images/container-security-pipeline.png">

---
## Tools:
- #### Open-source:
  + [Clair](https://github.com/quay/clair) - Vulnerability Static Analysis for Containers
  + [Anchore](https://anchore.com/opensource/) - Open-source project for deep analysis of docker images
  + [Dagda](https://github.com/eliasgranderubio/dagda/) - A tool to perform static analysis of known vulnerabilities, trojans, viruses, malware & other malicious   threats in docker images/containers and to monitor the docker daemon and running docker containers for detecting anomalous activities
  + [Falco](https://falco.org/) - Falco, the cloud-native runtime security project, is the de facto Kubernetes threat detection engine
  + [Harbor](https://goharbor.io/) - Harbor is an open source registry that secures artifacts with policies and role-based access control, ensures images are scanned and free from vulnerabilities, and signs images as trusted.
  + [Trivy](https://aquasecurity.github.io/trivy/) - Trivy is a simple and comprehensive vulnerability/misconfiguration scanner for containers and other artifacts.
  + [Kbescape](https://github.com/armosec/kubescape) - Kubescape is a K8s open-source tool providing a multi-cloud K8s single pane of glass, including risk analysis, security compliance, RBAC visualizer and image vulnerabilities scanning.
- #### Commercial:
  + [Aquasec](https://www.aquasec.com/products/container-vulnerability-scanning/) - With Aqua’s advanced vulnerability scanning & management DevOps can detect vulnerabilities, embedded secrets, and other risks during the development cycle, and prioritize mitigation by risk-based insights. Available on Aqua Enterprise, Self-hosted or SaaS.
---
### References

+ [Opensource.com - tools for container security](https://opensource.com/article/18/8/tools-container-security)
