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
