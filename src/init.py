import sys

title = sys.argv[1]
author = sys.argv[2]

tab = "    "

with open("main.tex", "w+") as f:
    f.write("\\documentclass{article}\n")
    f.write("\n")
    f.write("\\title{" + title + "}\n")
    f.write("\\author{" + author + "}\n")
    f.write("\n")
    f.write("\\begin{document}\n")
    f.write(tab + "\\maketitle\n")
    f.write("\\end{document}\n")


with open("README.md", "w+") as f:
    f.write("# " + title + "\n\n")
    f.write("* **[Latest release](https://github.com/georgejkaye/" +
            title + "/releases/latest)**\n")
    f.write("## Setting up\n\n")
    f.write(
        "This project uses *submodules* to share diagrams and things between repos.\n")
    f.write(
        "This means that the repo has a snapshot of another repo at a certain commit.")
    f.write("To make sure you have them all pulled, do this to initialise them:\n\n")
    f.write("```sh\n")
    f.write("git submodule update --init\n")
    f.write("git submodule foreach git checkout main\n")
    f.write("```\n\n")
    f.write("Now you can interact with the submodule as if it were its own repo, pushing and pulling as you like.\n")
    f.write("After making some commits in a submodule repo, you can use `git add` in the top repo to add those new commits to the main repo.\n\n")
    f.write("If someone else has changed the submodule to a different commit, you can update your local copy with \n\n")
    f.write("```sh\n")
    f.write("git submodule update\n")
    f.write("```\n\n")
    f.write("Alternatively you can set the following git option:\n")
    f.write("```sh\n\n")
    f.write("git config --global submodule.recurse true\n\n")
    f.write("```\n\n")
    f.write('## GitHub Actions\n\n')
    f.write(
        "Every time you push a commit to `main`, the latex will be compiled and put in a release.\n\n")
