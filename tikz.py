from pathlib import Path
import re
import os.path

from latex import invoke_latexmk

tikzfig_regex = (
    r"\\iltikzfig\{(.*?)\}(?:\[((?:.*?=.*?(?:\[.*?\])?\], ?)*.*?=.*?(?:\[.*?\])?)\])?"
)
tikzfigures_basename = "tikzfigures"
tikzfigures_file = f"{tikzfigures_basename}.tex"


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


def remove_tikz_tex_if_exists(output_path: Path):
    if os.path.exists(output_path):
        overwrite = input(f"File {output_path} already exists, overwrite? (y/N) ")
        if not overwrite == "y":
            exit(1)
        os.remove(output_path)


def append_to_tikz_tex(output_path: Path, content: str):
    with open(output_path, "a") as f:
        f.write(content)


def replace_tikzfigs_in_files(output_dir: Path, output_path: Path):
    for root, _, files in os.walk(output_dir):
        for file in files:
            file_path = Path(root) / file
            extension = file_path.suffix
            if extension == ".tex" and file != tikzfigures_file:
                replace_tikzfigs_in_file(file_path, output_path)


def get_tikz_preamble(input_dir: Path) -> str:
    with open(Path(input_dir) / "tikzpreamble.tex", "r") as f:
        preamble = f.read()
    return "\n".join(
        ["\\documentclass[multi=page]{standalone}", preamble, "\\begin{document}"]
    )


def replace_tikzfigs_in_output_dir(input_dir: Path, output_dir: Path):
    tikz_tex_path = Path(output_dir) / tikzfigures_file
    tikz_tex_preamble = get_tikz_preamble(input_dir)
    append_to_tikz_tex(tikz_tex_path, tikz_tex_preamble)
    replace_tikzfigs_in_files(output_dir, tikz_tex_path)
    append_to_tikz_tex(tikz_tex_path, "\\end{document}")
    invoke_latexmk(["-pdf", "-cd", tikz_tex_path])
    invoke_latexmk(["-c", "-cd", tikz_tex_path])
    os.remove(tikz_tex_path)
