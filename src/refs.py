import sys
import re
import os

bib = '(@[a-z]*{([a-z0-9]*),\n(.*\n)*?})'
fname = '(.*?).'

tex = sys.argv[1]
refdir = sys.argv[2]

if len(sys.argv) == 4:
    outp = sys.argv[3]
else:
    outp = "refs.bib"

bibs = []
keys = []
doclines = []

with open(tex) as f:
    doclines = [line.rstrip() for line in f]

for file in os.listdir(refdir):
    if file.endswith(".bib"):
        with open(os.path.join(refdir, file)) as f:
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
