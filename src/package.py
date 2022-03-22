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


def make_project_dir(project_name):
    if os.path.isdir(project_name):
        print(f"Directory {project_name} already exists, quitting...")
        exit(1)

    os.makedirs(project_name)


def copy_into_project(project_name, project_dir, file):
    original_path = os.path.join(project_dir, file)
    new_path = os.path.join(project_name, file)
    os.makedirs(os.path.dirname(new_path), exist_ok=True)
    print(f"Copying {os.path.abspath(original_path)} into project")
    shutil.copy2(original_path, new_path)


def copy_input_into_project(project_name, project_dir, file):
    full_path = os.path.join(project_dir, file)
    if not os.path.exists(full_path):
        full_path_tex = f"{full_path}.tex"
        if not os.path.exists(full_path_tex):
            print(
                f"Could not find input {full_path} or {full_path_tex}, quitting...")
            exit(1)
        else:
            full_path = full_path_tex
            file = f"{file}.tex"

    copy_into_project(project_name, project_dir, file)
    return full_path


def copy_tikzfig_into_project(project_name, project_dir, file):
    figure_path = os.path.join("figures", f"{file}.tikz")
    full_path = os.path.join(project_dir, "figures", f"{file}.tikz")
    if not os.path.exists(full_path):
        print(f"Could not find tikzfig {full_path}, quitting...")
    copy_into_project(project_name, project_dir, figure_path)


def process_file(project_name, project_dir, file):
    files = get_included_files(file)
    copied_files = []

    for file in files["input"]:
        copied_file = copy_input_into_project(project_name, project_dir, file)
        copied_files.append(copied_file)

    for file in files["tikzfig"]:
        copy_tikzfig_into_project(project_name, project_dir, file)

    return copied_files


def process_files(project_name, project_dir, frontier):
    if len(frontier) > 0:
        current_file = frontier.pop()
        copied_files = process_file(project_name, project_dir, current_file)
        frontier = [*frontier, *copied_files]
        process_files(project_name, project_dir, frontier)


def main(project_name, project_dir, root_file):

    full_root = check_project_exists(project_dir, root_file)

    make_project_dir(project_name)
    copy_into_project(project_name, project_dir, root_file)
    process_files(project_name, project_dir, [full_root])


args = ["project_name", "project_dir", "root_file"]

if __name__ == '__main__':
    if len(sys.argv) == len(args) + 1:
        project_name = sys.argv[1]
        project_dir = sys.argv[2]
        root_file = sys.argv[3]
        main(project_name, project_dir, root_file)
    else:
        print("Usage: package.py <project_name> <project_dir> <root_file>")
        exit(1)
