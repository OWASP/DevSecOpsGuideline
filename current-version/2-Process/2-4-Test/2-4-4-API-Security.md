# API Security

APIs are the connective tissue of modern applications — and the dominant attack surface. As architectures shift to microservices, mobile backends, and third-party integrations, most business logic and data is exposed through APIs. Attackers have followed, making API security a first-class testing concern rather than a subset of web testing. The 2023 Verizon DBIR and OWASP data consistently show API-related vulnerabilities in the top causes of breaches.

## The OWASP API Security Top 10

The [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/) frames the most critical API risks:

| Risk | Description | Why it is hard to catch |
|---|---|---|
| **BOLA/IDOR** (API1) | Accessing other users' objects by manipulating IDs | Requires testing with multiple user sessions; scanners cannot infer valid IDs |
| **Broken Authentication** (API2) | Weak or missing authentication on endpoints | Often found only on non-obvious or legacy endpoints |
| **Broken Object Property Level AuthZ** (API3) | Over-exposing or allowing modification of fields (mass assignment, excessive data exposure) | Requires comparing spec vs actual response |
| **Unrestricted Resource Consumption** (API4) | Missing rate limiting enabling abuse and DoS | Requires scripted load testing, not passive scanning |
| **Broken Function Level AuthZ** (API5) | Accessing admin/privileged functions without checks | Requires role-based test cases across all permission levels |
| **Unrestricted Access to Sensitive Business Flows** (API6) | Automating flows not intended for automation (e.g., bulk purchase, account takeover) | Logic-specific; tooling alone cannot detect |
| **SSRF** (API7) | Server-side request forgery via API parameters | Requires active payload injection and out-of-band detection |
| **Security Misconfiguration** (API8) | Default credentials, unnecessary endpoints, verbose error messages | Schema drift, debug flags, CORS wildcards |
| **Improper Inventory Management** (API9) | Shadow APIs, deprecated/zombie endpoints still live | Requires ongoing discovery, not point-in-time testing |
| **Unsafe API Consumption** (API10) | Trusting third-party API responses without validation | Requires review of every external integration |

## Testing and protecting APIs

### API discovery and inventory

You cannot protect what you do not know about. Maintain a live API inventory by:

- Parsing OpenAPI/AsyncAPI specs from source control.
- Passive traffic analysis in staging/production to detect shadow APIs (endpoints that receive traffic but are not in the spec).
- Regular crawls and traffic baselining to catch zombie APIs (deprecated endpoints still responding).

```bash
# Example: Use Akto to discover APIs from network traffic
# After mirroring traffic to Akto collector, view discovered endpoints at dashboard
```

### Schema and contract testing

The spec is a security contract. Test that the implementation matches it:

- **Positive testing** — valid requests return expected responses.
- **Negative testing** — invalid inputs, missing required fields, wrong types return proper error codes (not 500s or data leaks).
- **Boundary testing** — values at extremes (max length, integer overflow, empty strings).

Schemathesis auto-generates test cases from your OpenAPI/GraphQL spec and can run in CI as a gate.

### Authorization testing (BOLA/IDOR)

This is the #1 API risk and requires explicit test cases because scanners cannot derive valid object IDs:

1. Create two test accounts (User A, User B).
2. User A creates a resource; capture its ID.
3. Authenticate as User B and attempt to access/modify User A's resource using the same ID.
4. The API must return 403 or 404, not the resource data.

Automate this pattern for every resource type. Tools like Escape and Akto have some BOLA detection, but manual test cases covering your data model are essential.

### Fuzzing

Send malformed and boundary-value inputs to surface crashes and unexpected behavior:

- **Schema-based fuzzing** — Schemathesis generates inputs that violate schema constraints to find validation gaps.
- **Generative fuzzing** — tools like RESTler or custom Radamsa-based scripts send novel inputs to find crashes and logic flaws.
- **Parameter pollution** — duplicate parameters, arrays where scalars are expected, nested objects.

### API-aware DAST

Standard web DAST crawlers do not understand REST or GraphQL semantics. Feed the scanner your API spec:

```bash
# OWASP ZAP API scan from OpenAPI spec
docker run -v $(pwd):/zap/wrk/:rw \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-api-scan.py -t api-spec.yaml -f openapi \
  -r api-scan-report.html -x api-scan-report.xml
```

### Runtime protection and monitoring

Testing catches issues before release; runtime protection catches exploitation in production:

- API gateway policies: enforce authentication, rate limits, request size limits, and schema validation on every request.
- Anomaly detection: flag unusual access patterns (account enumeration, excessive data retrieval, parameter tampering).
- Continuous discovery: re-run inventory analysis against production traffic to catch new shadow APIs.

## Common pitfalls and anti-patterns

- **Relying only on authentication as the authorization check** — an authenticated user should not be able to access other users' resources. Auth and authz are separate.
- **Not testing with multiple user roles** — a single test account misses privilege escalation and BFLA (Broken Function Level Authorization).
- **Spec drift** — the OpenAPI spec is updated, but tests still cover the old contract. Automate spec-to-test synchronization.
- **Trusting the API gateway to do all security** — gateways enforce rate limits and authN, but BOLA and business logic flaws require application-layer validation.
- **Not monitoring for API abuse in production** — attacks on APIs are often slow and low-volume; signature-based WAFs miss them without behavioral baselines.

## Maturity progression

**Starter** — Maintain an OpenAPI spec for every API. Run OWASP ZAP API scan in CI against each build. Create BOLA test cases for the two most critical resources.

**Intermediate** — Add Schemathesis schema-validation testing in CI. Automate BOLA/IDOR test cases for all resource types. Deploy API gateway with rate limiting and schema enforcement. Run passive traffic discovery in staging.

**Advanced** — Continuous runtime traffic analysis to detect shadow/zombie APIs and anomalous access. Full OWASP API Top 10 test coverage automated per release. Correlation of API findings with application risk in ASPM. Red team exercises targeting API authorization logic.

## Metrics and KPIs

- **API inventory completeness** — percentage of known API endpoints that have a corresponding spec entry (higher = fewer shadow APIs).
- **BOLA/IDOR test coverage** — percentage of resource types with automated authorization test cases.
- **New high/critical API findings per release** — primary gate signal.
- **Shadow API count** — discovered endpoints not in the spec; should trend toward zero.
- **API gate pass rate** — percentage of builds where API tests pass without exceptions.

---

## Tools[^1]

### Open-source

- [Akto](https://github.com/akto-api-security/akto) — API discovery from network traffic and security testing; good for finding shadow APIs in staging environments.
- [OWASP ZAP](https://www.zaproxy.org/) — Supports API scanning from OpenAPI/SOAP/GraphQL definitions via `zap-api-scan.py`; strong CI integration.
- [Schemathesis](https://github.com/schemathesis/schemathesis) — Property-based API testing from OpenAPI/GraphQL spec; excellent for finding schema-validation bypass and server crashes.
- [RESTler](https://github.com/microsoft/restler-fuzzer) — Stateful REST API fuzzer from Microsoft Research; generates and executes sequences of API calls to find logic and resource-management flaws.

### Commercial

- [Escape](https://escape.tech/) — API discovery and dynamic security testing; strong GraphQL support and CI-native with developer-friendly findings.
- [Noname Security (Akamai API Security)](https://www.akamai.com/products/api-security) — API discovery, posture management, and runtime protection; strong on detecting anomalous access patterns in production traffic.
- [Salt Security](https://salt.security/) — API security platform for discovery and runtime defense; uses ML-based behavioral analysis to detect API-targeted attacks.
- [42Crunch](https://42crunch.com/) — API security audit from OpenAPI spec and runtime protection; integrates directly into the development workflow with IDE plugins.

---

### Links

[^1]: Listed in alphabetical order.
