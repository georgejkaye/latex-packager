
import re

# modes
INPUT = 0
STANDALONE = 1
BIBTEX = 2
BIBLATEX = 3
TIKZFIG = 4

# regexes
braces = '\{(.*?)\}'
input = 'input\{(.*?)\}'
standalone = 'includestandalone(?:\[.*?\])?' + braces
tikzfig = 'tikzfig' + braces
bibtex = 'bibliography\{(.*?)\}'
biblatex = 'addbibresource\{(.*?)\}'


def filter(mode, text):

    if mode == INPUT:
        regex = input
    elif mode == STANDALONE:
        regex = standalone
    elif mode == BIBTEX:
        regex = bibtex
    elif mode == BIBLATEX:
        regex = biblatex
    elif mode == TIKZFIG:
        regex = tikzfig
    else:
        print("Bad mode " + mode)
        quit()

    matches = re.findall(regex, text)

    if len(matches) > 0:
        matches = sorted(set(matches))
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

    return {
        "input": [*inputs, *standalones],
        "bibtex": bibtexes,
        "biblatex": biblatexes,
        "tikzfig": tikzfigs
    }
