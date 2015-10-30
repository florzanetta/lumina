#!/bin/bash

set -e
set -u

cd $(dirname $0)

for img in $(ls -1b images/ ) ; do
	if [ ! -e images-border/$img ] ; then
		echo "Adding border to $img"
		convert -border 3x3 -bordercolor "#AAAAAA" images/$img images-border/$img
	fi
done

make html

make latex

cd _build/latex

make

# _build/latex/Lumina.tex
