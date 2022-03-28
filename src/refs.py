import re
import os

bib = '(@[a-z]*\{([a-z0-9\-]*),\n(?:.*\n)*?\})'
fname = '(.*?).'


def get_used_refs(output_dir, project_dir, bibresources, refs):

    for resource in bibresources:
        resource_path = os.path.join(project_dir, resource)
        with open(resource_path) as f:
            text = f.read()

        matches = re.findall(bib, text)

        entries = []

        for match in matches:
            if not match in entries:
                entries.append(match)

        entries.sort(key=lambda m: m[1])
        used_entries = []

        for entry in entries:
            key = entry[1]
            if key in refs:
                used_entries.append(entry[0])

        output_path = os.path.join(output_dir, resource)
        with open(output_path, "w+") as f:
            for entry in used_entries:
                f.write(f"{entry}\n\n")
