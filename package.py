import os
from pathlib import Path
import re
import shutil
import sys
import subprocess

from bookmarks import get_section_numbers, split_pdf

args = ["input_dir", "root_file", "output_dir", "shell_escape", "chapters"]


def make_output_dir(output_dir):
    if os.path.isdir(output_dir):
        overwrite = input(
            "Directory " + output_dir + " already exists, overwrite? (y/N) "
        )
        if not overwrite == "y":
            exit(1)
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)


def move_and_replace(original_dir, file, new_dir):
    original_path = os.path.join(original_dir, file)
    new_path = os.path.join(new_dir, file)
    if os.path.isfile(new_path):
        os.remove(new_path)
    print(f"Moving {original_path} to {new_dir}")
    try:
        shutil.move(original_path, new_dir)
    except:
        print(f"{original_path} not found, continuing...")


def compile_latex(input_dir, root_file, output_dir, shell_escape):
    print("Compiling latex...")
    input_tex = os.path.join(input_dir, root_file + ".tex")
    # Clean first in case the last build was dodgy
    p = subprocess.run(["latexmk", "-c", "-cd", input_tex])
    # Build the document
    if shell_escape:
        shell_escape_string = "--shell-escape"
    else:
        shell_escape_string = ""
    p = subprocess.run(["latexmk", "-pdf", "-cd", shell_escape_string, input_tex])
    if p.returncode != 0:
        print("Could not compile document")
        exit(1)
    # Copy the root file into the output, as it's not imported in the log
    shutil.copy(input_tex, output_dir)
    # Store the log in the current working directory so we can use it later
    move_and_replace(input_dir, f"{root_file}.log", f"./{output_dir}.log")
    # Store the pdf in the current working directory so we can upload it
    move_and_replace(input_dir, f"{root_file}.pdf", f"./{output_dir}.pdf")


source_file_regex = r"\(\./([a-z0-9\-/\n]*\.([a-z0-9\n]*))"
binary_file_regex = r"<\.\/((?:[A-Za-z0-9\/_\-\.])*(?:\n.*)?),?"
svg_file_regex = r"svg-inkscape\/(.*)_svg-tex\.pdf"

no_copy_extensions = ["aux", "out", "nav", "w18"]


def make_dirs_and_copy_file(original_path, new_path):
    print(f"Copying {original_path} to {new_path}...")
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    shutil.copy(original_path, new_path)


def copy_files_into_project(input_dir, output_dir, output_root):
    print("Copying files into project...")
    # Open the log file
    output_log_file = f"{output_root}.log"
    with open(output_log_file, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()
    # Find the files that are included by the build process
    source_files = re.findall(source_file_regex, log_text)
    all_files = re.findall(binary_file_regex, log_text)
    for file in source_files:
        if file[1].replace("\n", "") not in no_copy_extensions:
            all_files.append(file[0])
    for file in all_files:
        # Sometimes the file names are spliced across lines
        file_name = file.replace("\npdf", "").replace("\n", "").replace("//", "/")
        original_file_path = os.path.join(input_dir, file_name)
        new_file_path = os.path.join(output_dir, file_name)
        make_dirs_and_copy_file(original_file_path, new_file_path)
        if "svg-inkscape" in file_name:
            svg_tex_file_name = f"{file_name}_tex"
            svg_tex_original_path = os.path.join(input_dir, svg_tex_file_name)
            svg_tex_new_path = os.path.join(output_dir, svg_tex_file_name)
            make_dirs_and_copy_file(svg_tex_original_path, svg_tex_new_path)
            svg_root_file_name = f"{re.findall(svg_file_regex, file_name)[0]}.svg"
            for root, dirs, files in os.walk(input_dir):
                if svg_root_file_name in files:
                    svg_input_path = Path(os.path.join(root, svg_root_file_name))
                    local_path = svg_input_path.relative_to(input_dir)
                    svg_output_path = Path(output_dir / local_path)
                    make_dirs_and_copy_file(svg_input_path, svg_output_path)


bib_file_regex = "Database file #[0-9]*: (.*)"
biber_file_regex = "Found BibTeX data source '(.*)'"
bibitem_regex = r"\\\\bibitem\[.*\]\{(.*)\}"
biberitem_regex = r"\\\\entry\{(.*?)\}"
bibentry_regex = r"(@[a-z]*\{([a-z0-9\-]*),\n(?:.*\n)*?\})"


def minimise_refs(input_dir, root_file, output_dir):
    print("Minimising refs...")
    # The bbl file lists the keys used
    bbl_file = os.path.join(output_dir, f"{root_file}.bbl")
    # The blg file lists the bibfiles used
    original_blg_file = os.path.join(input_dir, f"{root_file}.blg")
    # Make sure there actually is a bbl or blg file, otherwise we can skip
    if not (os.path.isfile(bbl_file) and os.path.isfile(original_blg_file)):
        print("No bbl or blg file found, skipping bibliography creation")
    else:
        with open(bbl_file) as bbl:
            bbl_text = bbl.read()
        used_bib_keys = re.findall(bibitem_regex, bbl_text)
        used_biber_keys = re.findall(biberitem_regex, bbl_text)
        used_keys = used_bib_keys + used_biber_keys
        with open(original_blg_file, "r") as blg:
            blg_data = blg.read()
        bib_files = re.findall(bib_file_regex, blg_data)
        biber_files = re.findall(biber_file_regex, blg_data)
        bib_sources = bib_files + biber_files
        # For each bib resource, find which entries in it are used
        for file in bib_sources:
            used_entries = []
            # Read the original bib resource
            input_path = os.path.join(input_dir, file)
            with open(input_path, "r") as bib:
                bib_text = bib.read()
            bib_entries = re.findall(bibentry_regex, bib_text)
            # Filter out the unused keys
            used_entries = list(
                map(
                    lambda x: x[0],
                    list(filter(lambda entry: entry[1] in used_keys, bib_entries)),
                )
            )
            # Write the used bib items to the new bib bile
            output_path = os.path.join(output_dir, file)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, "w") as w:
                for entry in used_entries:
                    w.write(entry)
                    w.write("\n")


def zip_package(output_dir):
    print("Zipping package...")
    subprocess.run(["zip", "-qq", "-r", f"{output_dir}.zip", output_dir])


def package_project(input_dir, root_file, output_dir, shell_escape, chapters):
    make_output_dir(output_dir)
    compile_latex(input_dir, root_file, output_dir, shell_escape)
    copy_files_into_project(input_dir, output_dir, output_dir)
    output_pdf = f"{output_dir}.pdf"
    minimise_refs(input_dir, root_file, output_dir)
    zip_package(output_dir)
    if chapters:
        bookmarks = get_section_numbers(output_pdf)
        chapter_dir = f"{output_dir}-chapters"
        make_output_dir(chapter_dir)
        split_pdf(output_pdf, bookmarks, f"{chapter_dir}/{output_dir}")
        zip_package(chapter_dir)


if __name__ == "__main__":
    if len(sys.argv) == len(args) + 1:
        input_dir = sys.argv[1]
        root_file = sys.argv[2]
        output_dir = sys.argv[3]
        shell_escape = bool(sys.argv[4])
        chapters = bool(sys.argv[5])
        package_project(input_dir, root_file, output_dir, shell_escape, chapters)
    else:
        print(f"Usage: package.py {' '.join(list(map(lambda x: f'<{x}>', args)))}")
        exit(1)
