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
    f.write(
        "This project uses *submodules* to share diagrams and things between repos.\n")
    f.write("To make sure you have them all pulled, do this to initialise them:\n\n")
    f.write("```sh\n")
    f.write("git submodule update --init\n")
    f.write("```\n\n")
    f.write("Occasionally you might want to do this to update the submodules:\n\n")
    f.write("```sh\n")
    f.write("git submodule foreach git pull origin main\n")
    f.write("```\n\n")
    f.write('## GitHub Actions\n\n')
    f.write(
        "Every time you push a commit starting with `[build]`, it will be compiled and put in a release.\n\n")
    f.write("## Latest release\n\n")
    f.write("* [PDF file](https://github.com/georgejkaye/" +
            title + "/releases/latest/download/" + title + ".pdf)\n")
    f.write("* [Source code](https://github.com/georgejkaye/" +
            title + "/releases/latest/download/" + title + ".zip)\n")
