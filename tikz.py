from pathlib import Path
import re
import subprocess
import os.path

tikzfig_regex = (
    r"\\iltikzfig\{(.*?)\}(?:\[((?:.*?=.*?(?:\[.*?\])?\], ?)*.*?=.*?(?:\[.*?\])?)\])?"
)
tikzfigures_basename = "tikzfigures"


matches = []


def replace_fn(tikz_output, match):
    global matches

    tikzfig_line = match.group(0)
    tikzfig_arg = match.group(1)
    tikzfig_params = match.group(2)

    if tikzfig_params is not None:
        tikzfig_params_suffix = (
            tikzfig_params.replace("\\", "")
            .replace(", ", "_")
            .replace(",", "_")
            .replace("=", "_")
            .replace("{", "_")
            .replace("}", "_")
            .replace("[", "_")
            .replace("]", "_")
            .replace("^", "_")
            .replace("(", "_")
            .replace(")", "_")
        )
    else:
        tikzfig_params_suffix = ""

    file_basename = f"{tikzfig_arg.replace('/', '_')}_{tikzfig_params_suffix}"

    if file_basename in matches:
        page_no = matches.index(file_basename) + 1
    else:
        matches.append(file_basename)
        page_no = len(matches)
        left_space = -0.1
        right_space = -0.4
        lines = [
            "\\begin{page}%",
            f"\\hspace{{{left_space}em}}{tikzfig_line}\\hspace{{{right_space}em}}%",
            "\\end{page}%",
        ]
        output = "\n".join(lines)

        with open(tikz_output, "a") as f:
            f.write(f"{output}\n")

    result = (
        f"\\adjustimage{{valign=c,margin=0pt,page={page_no}}}{{{tikzfigures_basename}}}"
    )

    return result


def replace_tikzfigs_in_string(tikz_output: Path, content: str) -> str:
    return re.sub(tikzfig_regex, lambda m: replace_fn(tikz_output, m), content)


def replace_tikzfigs_in_file(file_path, tikz_output):
    with open(file_path, "r") as f:
        content = f.read()
    print(f"Replacing tikzfigs in {file_path}...")
    new_content = replace_tikzfigs_in_string(tikz_output, content)
    with open(file_path, "w") as f:
        f.write(new_content)


def replace_tikzfigs_in_output_dir(input_dir, output_dir):
    with open(Path(input_dir) / "tikzpreamble.tex", "r") as f:
        preamble = f.read()

    content = "\n".join(
        ["\\documentclass[multi=page]{standalone}", preamble, "\\begin{document}"]
    )

    tikz_output = Path(output_dir) / f"{tikzfigures_basename}.tex"

    if os.path.exists(tikz_output):
        overwrite = input(f"File {tikz_output} already exists, overwrite? (y/N) ")
        if not overwrite == "y":
            exit(1)
        os.remove(tikz_output)

    with open(tikz_output, "w+") as f:
        f.write(content)

    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = Path(root) / file
            extension = file_path.suffix
            if extension == ".tex":
                replace_tikzfigs_in_file(file_path, tikz_output)

    with open(tikz_output, "a") as f:
        f.write("\\end{document}")

    p = subprocess.run(["latexmk", "-pdf", "-cd", tikz_output])
    if p.returncode != 0:
        print(f"Could not compile {tikz_output}")
        exit(1)

    for i, match in enumerate(matches):
        print(f"{i}: {match}")
