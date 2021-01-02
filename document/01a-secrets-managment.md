## Take care secrets and credentials in git repositories

After commit a pull request to a Git repo, How to can make sure about didn't push some credentials to the repo? 
We should find a way to scan your GitHub repository and detect any sensitive information such as password, secret key, confidential, etc.
Today if you go to bug bounties write-ups you can find a lot of reports related to this concern. Some credentials were hard-coded or pushed by a mistake. 

Here we want to explain some tools that can help us to do an automate scan to find out the sensitive data and make it repeatable and efficient based on our development pipeline customizations. 

## Tools:
#### 1- gittyleaks
Find sensitive information for a git repo [GitRepo](https://github.com/kootenpv/gittyleaks)
