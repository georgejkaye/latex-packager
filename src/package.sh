#!/bin/bash

# We assume a project layout as
# locs1970
# | - main.tex      The main latex file 
# | - sections      Supplementary latex files, included by \input
# | - macros        Macro files, included by \input
# | - figures       Tikz figures included by \tikzfig 
# | - tikz          Tikz figures included by \includestandalone



# name of the whole project, the resulting zip will be called this
PROJECT="$1"
# location of the project to package, we assume there is a main.tex in this directory
ROOT="$2"
# Original location of figures
FIGURES="$3"
# Original location of tikz
TIKZ="$4"

# put in the tex file
# TODO this might be multiple
cp $TEX $PROJECT

mkdir $PROJECT

# Sort out refs


# Sort out figures
function() 

    FIGS="figs.txt"
    python src/figs.py $TEX $FIGS

    FIGS_DIR="$PROJECT/figures"

    while IFS= read -r line; do
        DIR="$(dirname "${line}")" ; FILE="$(basename "${line}")"
        mkdir -p "$FIGS_DIR/$DIR"
        cp "$FIGURES/$line.tikz" "$FIGS_DIR/$line.tkz"
    done < $FIGS

zip -r $PROJECT.zip $PROJECT

rm $FIGS

