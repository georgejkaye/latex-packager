import sys
import re

bib = '(@[a-z]*{([a-z0-9]*),\n(.*\n)*?})'

file = sys.argv[1]
refs = sys.argv[2]

doclines = []

bibs = []

with open(file) as f:
    doclines = [line.rstrip() for line in f]

with open(refs) as rf:
    line = rf.read()
    matches = re.findall(bib, line)

    for match in matches:
        key = match[1]
        for l in doclines:
            if key in l:
                bibs.append(match[0])
                break

with open("refs.bib", "w") as f:
    for b in bibs[:-1]:
        f.write(b + "\n\n")
    f.write(bibs[-1])
