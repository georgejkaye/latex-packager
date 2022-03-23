import os
import sys
import shutil

from filter import get_included_files


def check_project_exists(project_dir, root_file):
    full_root = os.path.join(project_dir, root_file)
    if os.path.exists(full_root):
        return full_root
    print(f"Project root {full_root} does not exist, quitting...")
    exit(1)


def make_project_dir(output_dir):
    if os.path.isdir(output_dir):
        print(f"Directory {output_dir} already exists, quitting...")
        exit(1)

    os.makedirs(output_dir)


def copy_into_project(output_dir, project_dir, file):
    original_path = os.path.join(project_dir, file)
    new_path = os.path.join(output_dir, file)
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    print(f"Copying {os.path.abspath(original_path)} into project")
    shutil.copy2(original_path, new_path)
    return original_path


def copy_file_with_extension_into_project(output_dir, project_dir, file, extension):
    file = f"{file}{extension}"
    full_path = os.path.join(project_dir, file)
    if not os.path.exists(full_path):
        print(f"Could not find file {full_path}, quitting...")
        exit(1)
    return copy_into_project(output_dir, project_dir, file)


def copy_file_with_maybe_extension_into_project(output_dir, project_dir, file, extension):
    full_path = os.path.join(project_dir, file)
    if not os.path.exists(full_path):
        return copy_file_with_extension_into_project(output_dir, project_dir, file, extension)

    return copy_into_project(output_dir, project_dir, file)


def copy_tikzfig_into_project(output_dir, project_dir, file):
    figure_path = os.path.join("figures", file)
    return copy_file_with_extension_into_project(
        output_dir, project_dir, figure_path, ".tikz")


def process_file(output_dir, project_dir, file):
    files = get_included_files(file)
    copied_files = []

    for file in files["input"]:
        copied_file = copy_file_with_maybe_extension_into_project(
            output_dir, project_dir, file, ".tex")
        copied_files.append(copied_file)

    for file in files["tikzfig"]:
        copy_tikzfig_into_project(output_dir, project_dir, file)

    for file in files["package"]:
        copy_file_with_extension_into_project(
            output_dir, project_dir, file, ".sty")

    for file in files["bibtex"]:
        copy_file_with_maybe_extension_into_project(
            output_dir, project_dir, file, ".bib")

    for file in files["biblatex"]:
        copy_file_with_extension_into_project(
            output_dir, project_dir, file, "")

    return copied_files


def process_files(output_dir, project_dir, frontier):
    if len(frontier) > 0:
        current_file = frontier.pop()
        copied_files = process_file(output_dir, project_dir, current_file)
        frontier = [*frontier, *copied_files]
        process_files(output_dir, project_dir, frontier)


def copy_project_files(output_dir, project_dir, root_file):

    root_tex = f"{root_file}.tex"
    full_root = check_project_exists(project_dir, root_tex)

    make_project_dir(output_dir)
    copy_into_project(output_dir, project_dir, root_tex)
    process_files(output_dir, project_dir, [full_root])


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
