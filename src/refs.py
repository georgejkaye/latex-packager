import sys
import re
import os

bib = '(@[a-z]*\{([a-z0-9\-]*),\n(.*\n)*?\})'
fname = '(.*?).'

tex = sys.argv[1]
bibfile = sys.argv[2]
outp = sys.argv[3]
files = sys.argv[4:]

bibs = []
keys = []
doclines = []

with open(tex) as f:
    doclines = [line.rstrip() for line in f]

for file in files:
    with(open(file)) as f:
        newlines = [line.rstrip() for line in f]
        doclines = doclines + newlines

with open(bibfile) as f:
    text = f.read()
    ms = re.findall(bib, text)
    for m in ms:
        if not m in keys:
            keys.append(m)

keys.sort(key=lambda m: m[1])

for key in keys:
    for l in doclines:
        if key[1] in l:
            bibs.append(key[0])
            break

with open(outp, "w") as f:
    for b in bibs[:-1]:
        f.write(b + "\n\n")
    f.write(bibs[-1] + "\n")
