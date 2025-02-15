## Pre-commit

The Pre-commit phase is important because it can prevent security issues before they are submitted to a central (Git) repository.

Making sure that there are no secrets in the code, and that the code follows certain guidelines (According to the Linter rules) will result in a higher quality code.

In the following, we take a look into different types of pre-commit actions that are as follows:
1. Secrets Management
2. Linting Code

Pre-commit is a git feature that can be leveraged as part of the shift-left security appraoch where the developers are empowered to view the issues in the source code earlier in the SDLC process. When the developer runs a git-commit command to commit the code into their local repository, pre-commit hook check can be executed to look for code quality issues, hard-coded secrets, insecure code, etc..

It is to be noted that pre-commit hooks are at the developer's local repository level and not the remote repository commonly used by all the developers working on the same project/application. In such cases when it's required to prevent security issues before they are submitted to a remote/central (Git) repository pre-push hook or git-push checks can be configured. Refer: https://git-scm.com/docs/git-push

Another alternative approach to scan the source code for security issues (such as hardcoded-secrets, insecure code and vulnerable dependencies/opensource libraries) is the use of SAST/SCA IDE plugins. This works together with the IDEs used by developers while they write the code. Whereas, git-commit and git-push actions are used after the code is written by the developer. It is necessary to discern these distinct use-cases in order to implement the proper security controls at various levels.

The following image can give you a better view of what the pre-commit means and why we must consider it. 

![Pre Commit](/current-version/assets/images/pre-commit.png)

## Tools:

+ [Pre-Commit](https://pre-commit.com/) - A framework for managing and maintaining multi-language pre-commit hooks.


### References

+ [Wikipedia - Lint (software)](https://en.wikipedia.org/wiki/Lint_(software))
