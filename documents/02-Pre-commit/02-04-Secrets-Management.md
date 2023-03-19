# Take care secrets and credentials


*How can you ensure that sensitive information are not pushed to a repository?*

This is one of the [OWASP Top Ten issues](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure) and
several bug bounties write-ups are related to this kind of issue, eg hard-coded credentials pushed by mistake.

You should scan your commits and your repository, and detect any sensitive information such as password, secret key, confidential, etc.
following the process shown in the picture.
<br/>

The ideal approach is detecting and preventing the exposure of sensitive data before that they hit the repository,
because they are then visible in the history. In case of code hosting platforms, secrets can still linger 
on the web and be searchable after you remove them from the repository.

A complimentary approach is scanning the repo for sensitive information, and then remove them;
note that when a credential is leaked, it is already compromised and should be invalidated.

## Detecting secrets in several locations

- **Detecting existing secrets** by searching in a repository for existing secrets.
- **Using Pre-commit hooks** in order to prevent secrets for entering our code base.
- **Detecting secrets in a pipeline** .

## Why Detecting Secrets?

+ The secrets should not be hardcoded.
+ The secrets should not be unencrypted.
+ The secrets should not be stored in source code.
+ The code history does not contain inadvertent secrets.

## Where and when to Detect Secrets?
![Pre Commit](/documents/assets/images/pre-commit.png)


Well, the best location is the **pre-commit** location, This ensure that before a secret actually enters your code base, it is intercepted, and the developer or to committer gets a message. Another location is the build server or the **build** process. The build server retrieves source code, which is already committed and then it can analyze the source code where it contains new secrets or when it contains known secrets that the secrets are actually validated or audited.

---
Here are some helpful tools to automatically scan repositories for sensitive information.
Scans can be implemented directly in our pipeline, and be repeatable and efficient. 

## Tools:
- **Open-source**:
  + [gittyleaks](https://github.com/kootenpv/gittyleaks) - Find sensitive information for a git repo
  + [git-secrets](https://github.com/awslabs/git-secrets) - Prevents you from committing secrets and credentials into git repositories
  + [Repo-supervisor](https://github.com/auth0/repo-supervisor) - Scan your code for security misconfiguration, search for passwords and secrets
  + [truffleHog](https://github.com/dxa4481/truffleHog) - Searches through git repositories for high entropy strings and secrets, digging deep into commit history
  + [Git Hound](https://github.com/ezekg/git-hound) - Git plugin that prevents sensitive data from being committed
  + [Github Secret Scanning](https://docs.github.com/en/code-security/secret-scanning) - Github built in feature for secret detection
