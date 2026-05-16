from pathlib import Path
import shutil
import subprocess
from typing import Any


def invoke_latexmk(args: list[Any]):
    print(f"Running latexmk {' '.join([str(arg) for arg in args])}")
    p = subprocess.run(["latexmk"] + args)
    if p.returncode != 0:
        print("Latexmk invocation failed")
        exit(1)


def compile_latex(input_dir, root_file, output_dir, shell_escape):
    print("Compiling latex...")
    input_tex = Path(input_dir) / f"{root_file}.tex"
    # Clean first in case the last build was dodgy
    invoke_latexmk(["-c", "-cd", input_tex])
    # Build the document
    base_args = ["-pdf", "-cd", input_tex]
    if shell_escape:
        base_args.append("--shell-escape")
    invoke_latexmk(base_args)
