import os
import sys
import subprocess

from process import copy_project_files

args = ["output_dir", "project_dir", "root_file"]


def compile_latex(output_dir, root_file):
    input_tex = os.path.join(output_dir, root_file + ".tex")
    output_pdf = os.path.join(output_dir, root_file + ".pdf")
    # Compile the latex file
    subprocess.run(["latexmk", "-pdf", "-cd", input_tex])
    # Clean up after compilation, but keep the bbl (we need it for arxiv)
    subprocess.run(["latexmk", "-c", "-cd", input_tex])
    # We don't want to zip the pdf, but we do want to keep it around
    subprocess.run(["mv", output_pdf, "."])


def package_project(output_dir, project_dir, frontier):
    copy_project_files(output_dir, project_dir, frontier)
    compile_latex(output_dir, root_file)


if __name__ == '__main__':
    if len(sys.argv) == len(args) + 1:
        output_dir = sys.argv[1]
        project_dir = sys.argv[2]
        root_file = sys.argv[3]
        package_project(output_dir, project_dir, root_file)
    else:
        print("Usage: package.py <output_dir> <project_dir> <root_file>")
        exit(1)
