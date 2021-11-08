#!/bin/bash

# We assume a project layout as
# locs1970
# | - main.tex      The main latex file 
# | - sections      Supplementary latex files, included by \input
# | - macros        Macro files, included by \input
# | - figures       Tikz figures included by \tikzfig 
# | - tikz          Tikz figures included by \includestandalone
# | - refs          Refs folder, containing one or more bibs

# name of the whole project, the resulting zip will be called this
PROJECT="$1"
# location of the project to package, we assume there is a main.tex in this directory
ROOT="$2"
# location of scripts directory
SCRIPTS="$3"

NAME="main"
MAIN="$NAME.tex"
MAINTEX="$PROJECT/$MAIN"

SECS="sections"
REFS="refs"
TIKZ="tikz"

if [ -d $PROJECT ] ; then
    echo "Directory exists, quitting..."
    exit 1
fi

mkdir "$PROJECT"
mkdir "$PROJECT/$TIKZ"

# put in the main tex file
cp "$ROOT/$MAIN" "$PROJECT/"

TEMP="$PROJECT/temp.txt"

# function to run the script to find which files are used
filter() {

    TEX=$1
    MODE=$2
    DIRNAME=$3
    EXT=$4

    python $SCRIPTS/src/files.py $MODE $TEX $TEMP

    if [ -f "$TEMP" ] ; then
        while IFS= read -r LINE; do
            DIR="$(dirname "${LINE}")" #; FILE="$(basename "${LINE}")"
            mkdir -p "$PROJECT/$DIRNAME/$DIR"
            cp "$ROOT/$DIRNAME/$LINE$EXT" "$PROJECT/$DIRNAME/$LINE$EXT"
        done < "$TEMP"
        rm $TEMP
    fi
}

figures() {
    filter $1 "tikzfig" "figures" ".tikz"
}

tikz() {
    filter $1 "standalone" "" ".tex"
}

sections() {
    filter $1 "section" "sections" ".tex"
}

macros() {
    filter $1 "macros" "macros" ".tex"
}

tikzstyles() {
    filter $1 "tikzstyles" "figures" ""
}

refs() {
    filter $1 "refs" "refs" ".bib"
}

# first do everything for the main file
sections "$MAINTEX"
figures "$MAINTEX"
tikz "$MAINTEX"
macros "$MAINTEX"
tikzstyles "$MAINTEX"

FILES="$MAINTEX"

# process the sections
# we assume there are no sections, macros, styles or bibliographies in here
for FILE in "$PROJECT/$SECS"/* ; do 
    figures $FILE
    tikz $FILE
    FILES="$FILES $FILE"
done

# get minimal refs
python "$SCRIPTS/src/files.py" "refs" "$MAINTEX" $TEMP
mkdir "$PROJECT/$REFS"

# for each refs file found by the script, minimise it
if [ -f $TEMP ] ; then
    while IFS= read -r LINE; do
        python $SCRIPTS/src/refs.py $MAINTEX "$ROOT/$REFS/$LINE.bib" "$PROJECT/$REFS/$LINE.bib" $FILES
    done < $TEMP
fi

rm $TEMP

# miscellaneous files
cp "$ROOT/figures/tikzit.sty" "$PROJECT/figures/"
cp "$ROOT/tikz/quiver.sty" "$PROJECT/tikz/"

# build the project
cd $PROJECT
latexmk -pdf

# we don't want to zip the pdf, but we do need it for the release
mv $NAME.pdf ..

# delete everything except the bbl (we need it for arxiv)
rm *aux *blg *fdb_latexmk *fls *log *out

cd ..