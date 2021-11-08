# latex-scripts

This repo contains some scripts I wrote to make my life easier.

(They might have been done before, I don't care)

## `package.sh`

Bundles a latex file and all its dependencies into a minimal zip package.
Compatible with `tikzit` and tikzpictures included through `includestandalone`.
Also allows you to bundle in some macro files (although it currently does not minimise these).

Requires your latex project to be in a particular structure:

```sh
locs1970
| - main.tex      The main latex file 
| - sections      Supplementary latex files, included by \input
| - macros        Macro files, included by \input
| - figures       Tikz figures included by \tikzfig 
    | - style.tikzstyles
    | - tikzit.sty
| - tikz          Tikz figures included by \includestandalone
    | - quiver.sty
| - refs          Refs folder, containing one or more bibs
```

## `refs.py`


Parses a latex file and a bib file and makes a new bib file with only the references used in the latex file.

```sh
python refs.py paper.tex refs.bib
```
