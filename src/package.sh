#!/bin/bash

# Usage: package.sh <conference> <repo> <scripts dir> <bibtex|biblatex> <variant> 
#
# We assume a project layout as
# locs1970
# | - main.tex      The main latex file 
# | - sections      Supplementary latex files, included by \input
# | - macros        Macro files, included by \input
# | - figures       Tikz figures included by \tikzfig 
# | - tikz          Tikz figures included by \includestandalone
# | - refs          Refs folder, containing one or more bibs

# name of the whole project, this will be used to begin the file and zip name
PROJECT="$1"
# location of the project to package, we assume there is a main.tex in this directory
ROOT="$2"
# location of scripts directory
SCRIPTS="$3"
# whether we're using biblatex
BIBTEX="$4"
# whether we are compiling a variant
VARIANT="$5"

MAIN="main"
MAINFILE="$MAIN.tex"
MAINPATH="$ROOT/$MAINFILE"

if [[ $VARIANT == "" ]] ; then
    PACKAGE="$PROJECT"
else 
    PACKAGE="$PROJECT-$VARIANT"
    VARIANTFILE="$MAIN-$VARIANT.tex"
    VARIANTPATH="$ROOT/$MAIN-$VARIANT.tex"
fi

SECS="sections"
REFS="refs"
TIKZ="tikz"

if [ -d $PACKAGE ] ; then
    echo "Package directory $PACKAGE exists, quitting..."
    exit 1
fi

mkdir "$PACKAGE"
mkdir "$PACKAGE/$TIKZ"

# put in the main tex file
cp "$MAINPATH" "$PACKAGE/"

# if we're packaging a variant, add its pre-preamble
if [[ $NAME == "" ]] ; then
    cp "$VARIANTPATH" "$PACKAGE/"
fi

TEMP="$PACKAGE/temp.txt"

echo "Making package $PACKAGE"

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
            mkdir -p "$PACKAGE/$DIRNAME/$DIR"
            cp "$ROOT/$DIRNAME/$LINE$EXT" "$PACKAGE/$DIRNAME/$LINE$EXT"
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

biber() {
    filter $1 "biber" "refs" ".bib"
}

# first do everything for the main file
echo "Looking for included files in main file..."
if [ -d "$ROOT/sections" ] ; then
    sections "$MAINPATH"
fi
figures "$MAINPATH"
tikz "$MAINPATH"
macros "$MAINPATH"
tikzstyles "$MAINPATH"

FILES="$MAINPATH"

# process the sections
# we assume there are no sections, macros, styles or bibliographies in here
if [ -d "$ROOT/sections" ] ; then
    for FILE in "$PACKAGE/$SECS"/* ; do 
        echo "Looking for included files in $FILE..."
        figures $FILE
        tikz $FILE
        FILES="$FILES $FILE"
    done
fi

# get minimal refs
if [ $BIBTEX == "biber" ] ; then
    BIBMODE="biber"
else 
    BIBMODE="bibtex"
fi

python "$SCRIPTS/src/files.py" $BIBMODE $MAINPATH $TEMP
mkdir "$PACKAGE/$REFS"

# for each refs file found by the script, minimise it
if [ -f $TEMP ] ; then
    while IFS= read -r LINE; do
        if [ $BIBTEX == "biber" ] ; then
            BIBFILE=$LINE
        else 
            BIBFILE=$LINE.bib
        fi
        python $SCRIPTS/src/refs.py $MAINPATH "$ROOT/$REFS/$BIBFILE" "$PACKAGE/$REFS/$BIBFILE" $FILES
    done < $TEMP
    rm $TEMP
fi

# miscellaneous files
cp "$ROOT/figures/tikzit.sty" "$PACKAGE/figures/"
cp "$ROOT/tikz/quiver.sty" "$PACKAGE/tikz/"

# build the project
cd $PACKAGE
echo "Using latexmk to build the document..."
latexmk -quiet -pdf $VARIANTFILE

# we don't want to zip the pdf, but we do need it for the release
echo "Moving the compiled pdf out of the package..."
mv "main-$VARIANT.pdf" ..

# delete everything except the bbl (we need it for arxiv)
echo "Cleaning up..."
rm *aux *blg *fdb_latexmk *fls *log *out

cd ..