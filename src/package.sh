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

MAIN="main.tex"

SECS="sections"
REFS="refs"

if [ -d $PROJECT ] ; then
    echo "Directory exists, quitting..."
    exit 1
fi

mkdir $PROJECT

# put in the main tex file
cp "$ROOT/$MAIN" "$PROJECT/"

# function to run the script to find which files are used
filter() {

    TEX=$1
    MODE=$2
    DIRNAME=$3
    EXT=$4

    echo "Filtering $MODE with $TEX"

    TEMP="$PROJECT/temp.txt"

    python files.py $MODE $TEX $TEMP

    if [ -f "$TEMP" ] ; then

        while IFS= read -r LINE; do
            DIR="$(dirname "${LINE}")" #; FILE="$(basename "${LINE}")"
            mkdir -p "$PROJECT/$DIRNAME/$DIR"
            cp "$ROOT/$DIRNAME/$LINE.$EXT" "$PROJECT/$DIRNAME/$LINE.$EXT"
        done < $TEMP
        
        rm $TEMP
    fi
}

figures() {
    filter $1 "tikzfig" "figures" "tikz"
}

tikz() {
    filter $1 "standalone" "tikz" "tex"
}

sections() {
    filter $1 "section" "sections" "tex"
}

macros() {
    filter $1 "macros" "macros" "tex"
}


# first do everything for the main file
sections "$PROJECT/$MAIN"
figures "$PROJECT/$MAIN"
tikz "$PROJECT/$MAIN"
macros "$PROJECT/$MAIN"

FILES=$MAIN

ls "$PROJECT/$SECS"

for FILE in "$PROJECT/$SECS"/* ; do 
    echo "Processing $FILE"
    figures $FILE
    tikz $FILE
    macros $FILE
    FILES="$FILES $FILE"
done

# get minimal refs
for FILE in "$ROOT/$REFS" ; do
    NAME="$(basename "$FILE")"
    python refs.py $REFS $NAME $FILES
done

# miscellaneous files
cp "$ROOT/figures/tikzit.sty" "$PROJECT/figures/"
cp "$ROOT/figures/hypergraphs.tikzstyles" "$PROJECT/figures/"
cp "$ROOT/tikz/quiver.sty" "$PROJECT/tikz/"

#zip -r $PROJECT.zip $PROJECT