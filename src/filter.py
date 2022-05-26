
import re

# modes
INPUT = 0
STANDALONE = 1
BIBTEX = 2
BIBLATEX = 3
TIKZFIG = 4
STRINGS = 5
GRAPHS = 6
PACKAGE = 7
CITE = 8
PDF = 9
GRAPHICS = 10
CLASS = 11

# regexes
braces = '\{\s*(.*?)\s*\}'
options = '(?:\[.*?\])?'
input = 'input' + braces
standalone = 'includestandalone' + options + braces
tikzfig = 'tikzfig' + braces
strings = 'stringtikz' + braces
graphs = 'graphtikz' + braces
bibtex = 'bibliography' + braces
biblatex = 'addbibresource' + braces
package = 'usepackage' + braces
refs = 'cite' + braces
pdf = 'includepdf' + options + braces
graphics = 'includegraphics' + options + braces
docclass = 'documentclass' + options + braces

regexes = [input, standalone, bibtex, biblatex,
           tikzfig, strings, graphs, package, refs, pdf, graphics, docclass]


def filter(mode, text):

    try:
        regex = regexes[mode]
    except:
        print("Bad mode " + str(mode))
        exit(1)

    matches = re.findall(regex, text)

    if len(matches) > 0:
        matches = sorted(set(matches))

        if mode == PACKAGE:
            local_packages = []
            for match in matches:
                if "/" in match:
                    local_packages.append(match)
            matches = local_packages

        if mode == CITE:
            all_refs = []
            for match in matches:
                splitted = match.split(",")
                all_refs = all_refs + splitted
            matches = all_refs

        return matches

    return []


def get_included_files(file):
    with open(file) as f:
        text = f.read()

    inputs = filter(INPUT, text)
    standalones = filter(STANDALONE, text)
    bibtexes = filter(BIBTEX, text)
    biblatexes = filter(BIBLATEX, text)
    tikzfigs = filter(TIKZFIG, text)
    graphs = list(map(lambda x: "graphs/" + x, filter(GRAPHS, text)))
    strings = list(map(lambda x: "strings/" + x, filter(STRINGS, text)))
    packages = filter(PACKAGE, text)
    cite = filter(CITE, text)
    pdfs = filter(PDF, text)
    graphics = filter(GRAPHICS, text)
    classes = filter(CLASS, text)

    return {
        "input": inputs + standalones,
        "bibtex": bibtexes,
        "biblatex": biblatexes,
        "tikzfig": tikzfigs + graphs + strings,
        "package": packages,
        "refs": cite,
        "pdfs": pdfs,
        "graphics": graphics,
        "classes": classes
    }
