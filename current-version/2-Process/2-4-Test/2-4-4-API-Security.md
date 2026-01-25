# API Security

API security  focuses on identifying vulnerabilities and weaknesses in web APIs at the interface, data, and business-logic layers, using both automated tools and manual techniques. It builds on the OWASP API Security Top 10 by explicitly testing how APIs handle authentication, authorization, input validation, rate limiting, and interaction with third-party services.

API security testing can be performed in a black-box, gray-box, or white-box manner and is typically integrated into CI/CD pipelines for continuous feedback, as well as performed manually for high-risk or complex business flows. Automated API tests often rely on API specifications (for example, OpenAPI) to generate requests, validate responses, and fuzz parameters, while manual testing is used to explore abuse cases and business logic flaws that tools struggle to detect.

## Key Testing Techniques

As more important API testing techniques we can look at the following:

* **API-focused DAST** - Dynamic scanning and fuzzing of REST/GraphQL endpoints, including authentication and authorization paths
* **Contract and schema validation tests** - Ensuring requests and responses conform to defined schemas and do not expose excessive or unintended data
* **Business logic and authorization testing** - Aligned with OWASP API Security Top 10 (for example BOLA, function-level authorization, unrestricted resource consumption)

## Tools

### Open-source

* **ZED Attack Proxy** - OWASP ZAP supports API-aware scanning (including importing OpenAPI/Swagger definitions) and can be used to dynamically test REST and SOAP APIs
* **Nuclei** - Fast, template-driven scanner that can be used to test APIs for known vulnerability patterns using simple YAML templates
* **OWASP API Security Testing Framework** - Framework focused on detecting API vulnerabilities aligned with the OWASP API Security Top 10

### Commercial

* **StackHawk** - CI/CD-focused DAST platform built on ZAP with strong support for automated API discovery and testing of modern REST and GraphQL APIs
* **Bright Security** - DAST platform with API-centric testing capabilities, including support for importing API definitions and testing authenticated API flows
* **Noname Security or Salt Security** - API security platforms that combine discovery, testing, and runtime analysis to detect API vulnerabilities and abuse aligned to the OWASP API Security Top 10

## Links

* [OWASP API Security Project](https://owasp.org/www-project-api-security/)
* [OWASP Top 10 API Security Risks – 2023](https://owasp.org/API-Security/editions/2023/en/0x11-t10/)
* [API Testing Overview – OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/12-API_Testing/01-Testing_GraphQL)
