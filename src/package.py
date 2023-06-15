import os
import re
import shutil
import sys
import subprocess


args = ["output_dir", "input_dir", "root_file"]


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
        print("No bbl file found, continuing...")


def compile_latex(input_dir, root_file, output_dir):
    input_tex = os.path.join(input_dir, root_file + ".tex")
    # Clean first in case the last build was dodgy
    p = subprocess.run(["latexmk", "-c", "-cd", input_tex])
    # Build the document
    p = subprocess.run(["latexmk", "-pdf", "-cd", input_tex])
    if p.returncode != 0:
        print("Could not compile document")
        exit(1)
    # Copy the root file into the output, as it's not imported in the log
    shutil.copy(input_tex, output_dir)
    if not input_dir == ".":
        # Store the log in the current working directory so we can use it later
        move_and_replace(input_dir, f"{root_file}.log", ".")
        move_and_replace(input_dir, f"{root_file}.blg", ".")
        # Store the pdf in the current working directory so we can upload it
        move_and_replace(input_dir, f"{root_file}.pdf", ".")


source_file_regex = "\(\./([a-z0-9\-/\n]*\.([a-z\n]*))"
binary_file_regex = "<\./(.*?)(?:>|,)"

no_copy_extensions = ["aux", "out", "nav"]


def copy_files_into_project(input_dir, root_file, output_dir):
    # Open the log file
    output_log_file = root_file + ".log"
    with open(output_log_file, "r", encoding="utf-8", errors="ignore") as f:
        log_text = f.read()
    # Find the files that are included by the build process
    source_files = re.findall(source_file_regex, log_text)
    all_files = re.findall(binary_file_regex, log_text)
    for file in source_files:
        if not file[1].replace("\n", "") in no_copy_extensions:
            all_files.append(file[0])
    for file in all_files:
        # Sometimes the file names are spliced across lines
        file_name = file.replace("\npdf", "").replace("\n", "").replace("//", "/")
        original_file_path = os.path.join(input_dir, file_name)
        new_file_path = os.path.join(output_dir, file_name)
        print(f"Copying {original_file_path} to {new_file_path}")
        os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
        shutil.copy(original_file_path, new_file_path)


bib_file_regex = "Database file #[0-9]*: (.*)"
biber_file_regex = "Found BibTeX data source '(.*)'"
bibitem_regex = "\\\\bibitem\{(.*)\}"
biberitem_regex = "\\\\entry\{(.*?)\}"
bibentry_regex = "(@[a-z]*\{([a-z0-9\-]*),\n(?:.*\n)*?\})"


def minimise_refs(input_dir, root_file, output_dir):
    # First open the bbl file to find which keys are used
    bbl_file = os.path.join(output_dir, f"{root_file}.bbl")
    # Make sure there actually is a bbl file, otherwise we can skip
    if os.path.exists(bbl_file):
        with open(bbl_file) as bbl:
            bbl_text = bbl.read()
        used_bib_keys = re.findall(bibitem_regex, bbl_text)
        used_biber_keys = re.findall(biberitem_regex, bbl_text)
        used_keys = used_bib_keys + used_biber_keys
        # Now open the blg file to find which bib resources are used
        blg_file = f"{root_file}.blg"
        with open(blg_file, "r") as blg:
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


def package_project(input_dir, root_file, output_dir):
    make_output_dir(output_dir)
    compile_latex(input_dir, root_file, output_dir)
    copy_files_into_project(input_dir, root_file, output_dir)
    minimise_refs(input_dir, root_file, output_dir)


if __name__ == "__main__":
    if len(sys.argv) == len(args) + 1:
        input_dir = sys.argv[1]
        root_file = sys.argv[2]
        output_dir = sys.argv[3]
        package_project(input_dir, root_file, output_dir)
    else:
        print("Usage: package.py <input_dir> <root_file> <output_dir>")
        exit(1)
