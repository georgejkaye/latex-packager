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


def get_latexmk_engine_argument(engine):
    if engine == "pdflatex":
        return None
    if engine == "lualatex":
        return "--pdflua"
    if engine == "xelatex":
        return "--xelatex"
    raise RuntimeError(f"Latex engine {engine} not supported")


def compile_latex(input_dir, root_file, engine, shell_escape):
    engine_argument = get_latexmk_engine_argument(engine)
    print(f"Compiling latex with {engine}...")
    input_tex = Path(input_dir) / f"{root_file}.tex"
    # Clean first in case the last build was dodgy
    invoke_latexmk(["-c", "-cd", input_tex])
    # Build the document
    base_args = ["-pdf", "-cd", input_tex]
    if shell_escape:
        base_args.append("--shell-escape")
    if engine_argument is not None:
        base_args.append(engine_argument)
    invoke_latexmk(base_args)
