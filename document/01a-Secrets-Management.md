## Take care secrets and credentials in git repositories

<img align="right" width="180" height="200" src="/document/assets/images/Cred scanning.png">
After commit a pull request to a Git repo, <em>How to can make sure about didn't push some credentials to the repo?</em>
We should find a way to scan your GitHub repository and detect any sensitive information such as password, secret key, confidential, etc.
Today if you go to bug bounties write-ups you can find a lot of reports related to this concern. Some credentials were hard-coded or pushed by a mistake. 
Today if you go to bug bounties write-ups you can find a lot of reports related to this concern. Some credentials were hard-coded or pushed by a mistake. In a simple and ideal logic perspective this process is something like the picture.<br/>

The ideal approach is detecting and preventing push sensitive data before storing into the git repo (Because basically, you can find all pushed data in the git history) BTW, another method is scanning the git repo find and change them before public leakage. 

---
Here we want to explain some tools that can help us to do an automate scan to find out the sensitive data and make it repeatable and efficient based on our development pipeline customizations. 

## Tools:
#### 1- gittyleaks
Find sensitive information for a git repo [GitRepo](https://github.com/kootenpv/gittyleaks)
+ **gittyleaks** Find sensitive information for a git repo. [GitRepo](https://github.com/kootenpv/gittyleaks)
+ **git-secrets** Prevents you from committing secrets and credentials into git repositories. [GitRepo](https://github.com/awslabs/git-secrets)
+ **Repo-supervisor** Scan your code for security misconfiguration, search for passwords and secrets. [GitRepo](https://github.com/auth0/repo-supervisor)
+ **truffleHog** Searches through git repositories for high entropy strings and secrets, digging deep into commit history. [GitRepo](https://github.com/dxa4481/truffleHog)
+ **Git Hound** Git plugin that prevents sensitive data from being committed. [GitRepo](https://github.com/ezekg/git-hound)