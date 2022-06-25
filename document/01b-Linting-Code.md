## Linting Code

### What Is Linting?  
Linting is the automated checking of your source code for programmatic and stylistic errors. This is done by using a lint tool (otherwise known as linter). A lint tool is a basic static code analyzer.

### What can Linting do?
- Linting can **detect errors** in a code and errors that can lead to a security vulnerabilities.
- Linters Can Also **detect formatting or styling issues** and makes the code more readable for more secure code.
- Linters can **suggest best practices**.
- Also they can **increases overall quality of the code**.
- Since everybody follows the same linting rules it **makes maintenance of code easier**.


### Basic Lint Tools
Lint tools are the most basic form of static analysis. Using lint tools can be helpful for identifying common errors, such as:
- Indexing beyond arrays.
- Dereferencing null pointers.
- (Potentially) dangerous data type combinations.
- Unreachable code.
- Non-portable constructs.

### Advanced Static Analysis Tools
Advanced static analysis tools typically deliver:
- Pattern-based simulation.
- Quality and complexity metrics.
- Best practice recommendations for developers.
- Support for multiple safety and security-focused coding standards.
- Out-of-the-box certification for use in the development of safety-critical applications.

### Issues with Linters
+ Not every language has "quality" standard linter tools available, each framwork usually has one or several linters.
+ Different versions or configurations can lead to different results.
+ Since some linters are very verbose and information overload can lead to focusing on "unimportant" issues.

### Where and When to Use Linter
![Pre Commit](/document/assets/images/Pre-commit.png) 

You can perform it in the **pre-commit** phase, so locally before actually committing code to your local repository to your local clone. Another phase where you often see linting is during the **build** phase, So here the build server pulls the code from the Git repository and performs linting on it and reports back that results from linting phase.


### References

+ [Preforce](https://www.perforce.com/blog/qac/what-lint-code-and-why-linting-important)