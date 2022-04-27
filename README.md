# latex-scripts

This repo contains some scripts I wrote to make my life easier.

(They might have been done before, I don't care)

## `init.py`

Initialises an empty latex file and readme, using a given title and author.
This is designed to work with my personal `latex-template` github template.

The readme details how to handle the submodules, and contains a link to the latest release.

## `package.py`

Bundles a latex file and all its dependencies into a minimal zip package.

```py
python package.py output_dir input_dir main
```

## `refs.py`

Parses a latex file and a bib file and makes a new bib file with only the references used in the latex file.

```sh
python refs.py paper.tex refs.bib
```
