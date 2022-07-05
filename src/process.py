import subprocess
import os
import sys
import shutil

from filter import get_included_files
from refs import get_used_refs


def check_project_exists(project_dir, root_file):
    full_root = os.path.join(project_dir, root_file)
    if os.path.exists(full_root):
        return full_root
    print("Project root " + full_root + " does not exist, quitting...")
    exit(1)


def make_project_dir(output_dir):
    if os.path.isdir(output_dir):
        print("Directory " + output_dir + " already exists, quitting...")
        exit(1)

    os.makedirs(output_dir)


def copy_into_project(output_dir, project_dir, file):
    original_path = os.path.join(project_dir, file)
    new_path = os.path.join(output_dir, file)
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    print("Copying " + os.path.abspath(original_path) + " into project")
    try:
        shutil.copy2(original_path, new_path)
    except:
        print(f"Could not copy file {original_path}, exiting...")
        exit(1)
    return {
        "copied_file": original_path,
        "relative_file": file
    }


def compile_sublatex_and_copy(output_dir, project_dir, file):
    tex = os.path.join(project_dir, f"{file}.tex")
    pdf = f"{file}.pdf"
    subprocess.run(["latexmk", "-pdf", "-cd", tex])
    copy_into_project(output_dir, project_dir, pdf)


def copy_file_with_extension_into_project(output_dir, project_dir, file, extension, allow_fail=False):
    file = file + extension
    full_path = os.path.join(project_dir, file)
    if not os.path.exists(full_path):
        if allow_fail:
            return None
        print("Could not find file " + full_path + " quitting...")
        exit(1)
    return copy_into_project(output_dir, project_dir, file)


def copy_file_with_maybe_extension_into_project(output_dir, project_dir, file, extension):
    full_path = os.path.join(project_dir, file)
    if not os.path.exists(full_path):
        return copy_file_with_extension_into_project(
            output_dir, project_dir, file, extension)

    return copy_into_project(output_dir, project_dir, file)


def copy_tikzfig_into_project(output_dir, project_dir, file):
    figure_path = os.path.join("figures", file)
    return copy_file_with_extension_into_project(
        output_dir, project_dir, figure_path, ".tikz")


def process_file(output_dir, project_dir, file):
    files = get_included_files(file)
    copied_files = []
    bibresources = []

    for file in files["input"]:
        copied = copy_file_with_maybe_extension_into_project(
            output_dir, project_dir, file, ".tex")
        copied_files.append(copied["copied_file"])

    for file in files["tikzfig"]:
        copy_tikzfig_into_project(output_dir, project_dir, file)

    for file in files["package"]:
        copy_file_with_extension_into_project(
            output_dir, project_dir, file, ".sty")

    for file in files["bibtex"]:
        copied = copy_file_with_maybe_extension_into_project(
            output_dir, project_dir, file, ".bib")
        bibresources.append(copied["relative_file"])

    for file in files["biblatex"]:
        copied = copy_file_with_extension_into_project(
            output_dir, project_dir, file, "")
        bibresources.append(copied["relative_file"])

    for file in files["pdfs"]:
        compile_sublatex_and_copy(output_dir, project_dir, file)

    for file in files["graphics"]:
        copy_file_with_maybe_extension_into_project(
            output_dir, project_dir, file, ".jpg")

    for file in files["classes"]:
        copy_file_with_extension_into_project(
            output_dir, project_dir, file, ".cls", True)

    refs = files["refs"]

    return {
        "copied": copied_files,
        "bibresources": bibresources,
        "refs": refs
    }


def process_files(output_dir, project_dir, frontier, bibresources, refs):
    if len(frontier) > 0:
        current_file = frontier.pop()
        copied = process_file(output_dir, project_dir, current_file)
        for file in copied["copied"]:
            if file not in frontier:
                frontier.append(file)

        for resource in copied["bibresources"]:
            if resource not in bibresources:
                bibresources.append(resource)
        for ref in copied["refs"]:
            if ref not in refs:
                refs.append(ref)

        return process_files(output_dir, project_dir, frontier, bibresources, refs)
    else:
        return {
            "bibresources": bibresources,
            "refs": refs
        }


def copy_project_files(output_dir, project_dir, root_file):

    root_tex = root_file + ".tex"
    full_root = check_project_exists(project_dir, root_tex)

    make_project_dir(output_dir)
    copy_into_project(output_dir, project_dir, root_tex)
    process_output = process_files(
        output_dir, project_dir, [full_root], [], [])
    bibresources = process_output["bibresources"]
    refs = process_output["refs"]
    get_used_refs(output_dir, project_dir, bibresources, refs)


args = ["output_dir", "project_dir", "root_file"]

if __name__ == '__main__':
    if len(sys.argv) == len(args) + 1:
        output_dir = sys.argv[1]
        project_dir = sys.argv[2]
        root_file = sys.argv[3]
        copy_project_files(output_dir, project_dir, root_file)
    else:
        print("Usage: copy.py <output_dir> <project_dir> <root_file>")
        exit(1)
