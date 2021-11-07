import sys
import re
import os

bib = '(@[a-z]*{([a-z0-9]*),\n(.*\n)*?})'
fname = '(.*?).'

refs = sys.argv[1]
outp = sys.argv[2]
files = sys.argv[3:]

bibs = []
keys = []
doclines = []

for file in files:
    with open(file) as f:
        doclines = [line.rstrip() for line in f]

with open(refs) as f:
    text = f.read()
    ms = re.findall(bib, text)
    for m in ms:
        if not m in keys:
            keys.append(m)

keys.sort(key=lambda m: m[1])

for key in keys:
    print(key[1])
    for l in doclines:
        if key[1] in l:
            bibs.append(key[0])
            break

print("Writing minimal bib file to " + outp)

with open(outp, "w") as f:
    for b in bibs[:-1]:
        f.write(b + "\n\n")
    f.write(bibs[-1])
