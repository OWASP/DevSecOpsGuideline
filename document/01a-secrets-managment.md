## Take care secrets and credentials in git repositories

<img align="right" width="180" height="200" src="/document/assets/images/Cred scanning.png">
After commiting a pull request to a repository, <em>How to ensure that you didn't push sensitive information?</em>

This is one of the [OWASP Top Ten issues](https://owasp.org/www-project-top-ten/2017/A3_2017-Sensitive_Data_Exposure) and
several bug bounties write-ups are related to this kind of issue, eg hard-coded credentials pushed by mistake.

You should scan your repository and detect any sensitive information such as password, secret key, confidential, etc.
In a simple and ideal logical perspective, this process is something like the picture.<br/>

The ideal approach is detecting and preventing the exposure of sensitive data before that they make it into the repo
(because basically, you can find all pushed data in the git history).
A complimentary approach is scanning the repo for sensitive information, and then remove them;
note that when a credential is stored in a repository, it is already compromised and should be invalidated.

---

Here are some helpful tools to automatically scan repositories for sensitive information.
Scans can be implemented directly in our pipeline, and be repeatable and efficient. 

## Tools:
+ **gittyleaks** Find sensitive information for a git repo. [GitRepo](https://github.com/kootenpv/gittyleaks)
+ **git-secrets** Prevents you from committing secrets and credentials into git repositories. [GitRepo](https://github.com/awslabs/git-secrets)
+ **Repo-supervisor** Scan your code for security misconfiguration, search for passwords and secrets. [GitRepo](https://github.com/auth0/repo-supervisor)
+ **truffleHog** Searches through git repositories for high entropy strings and secrets, digging deep into commit history. [GitRepo](https://github.com/dxa4481/truffleHog)
+ **Git Hound** Git plugin that prevents sensitive data from being committed. [GitRepo](https://github.com/ezekg/git-hound)
