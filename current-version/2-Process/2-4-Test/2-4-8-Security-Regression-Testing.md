# Security Regression Testing

A security regression is a vulnerability that was fixed once and comes back: a refactor drops an authorization check, a new endpoint copies an old unsafe pattern, or a library upgrade changes a secure default. Scanners rarely catch these. SAST does not know your authorization model, and DAST does not know that `GET /api/orders/1001` must return 404 for Bob. The team that fixed the bug is the only one that knows exactly what "fixed" means, so that knowledge has to be written down as an automated test.

Security regression testing turns security requirements, abuse cases, and past vulnerabilities into ordinary unit, integration, and policy tests that run on every change. They use the same test frameworks the team already has, run in seconds, and fail the build in the same way as any other broken test.

## What to cover

- **Every fixed vulnerability.** Each security fix ships with a test that reproduces the original attack and fails on the vulnerable code. This applies to findings from pentests, bug bounty reports, scanners, and incidents alike.
- **Authorization rules.** Broken access control is the most common class of web vulnerability, and it is mostly logic that only your own tests can check. Test that each role can do what it should and nothing more, and that one user cannot reach another user's objects (BOLA/IDOR).
- **Abuse cases.** The abuse cases written next to user stories (see [Secure Design and Requirements](../2-1-Design/2-1-2-Secure-design-and-requirements.md)) make good test cases: replaying a password reset token, skipping a step in a checkout flow, or exceeding a rate limit.
- **Security controls and settings.** Security headers, cookie flags, session timeout, CSRF protection, TLS settings, and error messages that must not leak internals. These break quietly when a framework or middleware changes.
- **Input handling.** Known payloads that once caused injection, path traversal, or deserialization issues, sent to the code paths that handle them.
- **Policies and infrastructure rules.** Admission control policies, IaC rules, and cloud guardrails are code too, and a policy that silently stops matching is a regression. See [Policy as Code](../../3-Governance/3-1-Compliance-Auditing/3-1-2-Policy-as-code.md).

## Writing the tests

### A test for every fix

Write the test before or together with the fix, and check that it fails without the fix. Name it after the ticket or advisory so the reason it exists is obvious later:

```go
// Regression test for SEC-123: "../" in the file name escaped the upload directory.
func TestDownloadRejectsPathTraversal(t *testing.T) {
    srv := newTestServer(t)
    for _, name := range []string{"../etc/passwd", "/etc/passwd", `..\..\windows\win.ini`, "a/../../b"} {
        resp, err := http.Get(srv.URL + "/download?name=" + url.QueryEscape(name))
        require.NoError(t, err)
        resp.Body.Close()
        assert.Equal(t, http.StatusBadRequest, resp.StatusCode, name)
    }
}
```

Test the behavior an attacker would see (the request is rejected or the data is not returned), not the internal function that happened to contain the bug, so the test still holds after the code is refactored.

### Authorization matrix tests

Describe who may do what in a table and let one test walk through it. Adding an endpoint then means adding rows, and a missing check shows up as a failing row:

```python
import pytest

CASES = [
    # user,       method,   path,                  expected status
    ("alice",     "GET",    "/api/orders/1001",    200),  # her own order
    ("bob",       "GET",    "/api/orders/1001",    404),  # another user's order
    ("anonymous", "GET",    "/api/orders/1001",    401),
    ("bob",       "DELETE", "/api/admin/users/7",  403),  # not an admin
    ("admin",     "DELETE", "/api/admin/users/7",  204),
]

@pytest.mark.parametrize("user,method,path,expected", CASES)
def test_access_matrix(client, auth_headers, user, method, path, expected):
    resp = client.request(method, path, headers=auth_headers(user))
    assert resp.status_code == expected
```

Run the matrix against a real application instance with seeded test data, not against mocks of the authorization layer, otherwise the test only checks the mock.

### Policy tests

Policy engines have their own test runners. A test that proves a privileged pod is still denied protects the admission policy from being weakened by accident:

```rego
package kubernetes.admission_test

import data.kubernetes.admission

privileged_pod := {"request": {"kind": {"kind": "Pod"}, "object": {"spec": {"containers": [
    {"name": "app", "securityContext": {"privileged": true}},
]}}}}

test_privileged_pod_denied if {
    count(admission.deny) > 0 with input as privileged_pod
}
```

Run Rego tests with `opa test`, Kyverno policies with `kyverno test`, and configuration files with Conftest.

### Variant rules

A test protects the place where the bug was found. To catch the same mistake elsewhere in the codebase, turn the vulnerable pattern into a custom SAST rule (for example in Semgrep or CodeQL) and run it with the rest of [SAST](../2-3-Build/2-3-1-Static-Analysis/2-3-1-1-Static-Application-Security-Testing.md). A rule like "file paths built from request parameters without the safe join helper" finds the variants of a path traversal bug that a single test cannot.

## Running them in the pipeline

- Run security regression tests in the normal unit and integration test stages, not in a separate security job that people learn to ignore. A failing security test should block the merge like any other failing test, and should not be suppressible through the scanner exception process described in [Security Gates](../2-3-Build/2-3-5-Security-Gates.md).
- Tag or name the tests (for example a `security` marker in pytest, or a `Security` prefix) so their results can be reported separately and their coverage tracked.
- Make adding a regression test part of the definition of done for security fixes, and check it in the code review of the fix.
- Feed the results into [vulnerability management](../2-7-Operate/2-7-4-Vulnerability-Management.md): a security test that starts failing again is a reopened vulnerability, not a flaky test.

## Common pitfalls and anti-patterns

- **Fixing without a test.** The fix is reviewed once, then nothing protects it. Most regressions come back during refactors months later.
- **Testing the wrong layer.** A unit test of a helper function passes while the endpoint that should call it no longer does. Test from the outside in, at least for authorization.
- **Only testing the happy path.** Tests that check what users can do, but never what they cannot do, miss broken access control entirely.
- **Mocking the security control.** Mocking out the authorization middleware or the policy engine makes the test pass by construction.
- **Marking security tests as flaky and skipping them.** If a security test is unreliable, fix the test; skipping it removes the protection silently.
- **Keeping the knowledge in tickets.** A pentest report or bug bounty finding that is not turned into a test is forgotten the next time the code changes.

## Maturity progression

**Starter** - Every security fix ships with a test that reproduces the original issue. Security headers and cookie flags are checked in an integration test.

**Intermediate** - An authorization matrix covers every API endpoint and role, and new endpoints are not merged without rows in it. Admission and IaC policies have their own tests. Pentest and bug bounty findings are turned into tests as part of closing them.

**Advanced** - Abuse cases from design reviews become tests before the feature ships. Each fixed vulnerability class is also captured as a custom SAST rule to find variants. Coverage of security tests is reported per service, and a reopened vulnerability triggers a root cause review.

## Metrics and KPIs

- **Fixes with a regression test (%)** - share of closed security findings that have an automated test; aim for 100% for high and critical.
- **Reintroduced vulnerabilities** - number of findings that were closed and later reported again; should trend to zero.
- **Authorization matrix coverage** - share of endpoints and roles covered by access control tests.
- **Policy test coverage** - share of admission, IaC, and cloud policies with at least one passing and one failing test case.
- **Skipped or disabled security tests** - should stay at zero; each one is an unprotected control.

---

## Tools[^1]

### Open-source

- [Conftest](https://github.com/open-policy-agent/conftest) - Tests structured configuration files (Kubernetes, Terraform, Dockerfiles, and more) against Rego policies in CI.
- [Kyverno CLI](https://kyverno.io/docs/kyverno-cli/) - Runs `kyverno test` against Kyverno policies with expected pass and fail resources.
- [Open Policy Agent](https://www.openpolicyagent.org/docs/policy-testing) - `opa test` runs unit tests for Rego policies, with coverage reporting.
- [Playwright](https://playwright.dev/) - Browser automation for end-to-end tests of login, session, and CSRF flows, and of headers and cookies as the browser sees them.
- [REST Assured](https://rest-assured.io/) - Java DSL for API tests, useful for access control matrices in JVM projects.
- [Semgrep Community Edition](https://github.com/semgrep/semgrep) - Custom rules that capture a fixed vulnerability pattern and find its variants across the codebase.
- [ZAP](https://www.zaproxy.org/) - Scripted scans and automation framework plans that replay known attack requests against a running application.

### Commercial

- [GitHub CodeQL](https://codeql.github.com/) - Query language for variant analysis; write a query from a fixed bug and run it across one or many repositories. Free for public repositories, part of GitHub Advanced Security for private ones.

---

### Links

- [OWASP Application Security Verification Standard](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Abuse Case Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Abuse_Case_Cheat_Sheet.html)
- [OWASP Authorization Testing Automation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Testing_Automation_Cheat_Sheet.html)

[^1]: Listed in alphabetical order.
