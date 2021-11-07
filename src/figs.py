import sys
import re

file = sys.argv[1]

if len(sys.argv) == 3:
    outp = sys.argv[2]
else:
    outp = "figs.txt"


tikzfig = 'tikzfig\{(.*?)\}'

with open(file) as f:
    text = f.read()
    matches = re.findall(tikzfig, text)

matches = sorted(set(matches))

with open(outp, "w") as f:
    for m in matches[1:]:
        f.write(m + "\n")
