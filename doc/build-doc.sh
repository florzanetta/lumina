#!/bin/bash

set -e
set -u

cd $(dirname $0)

for img in $(ls -1b images/ ) ; do
	if [ ! -e images-border/$img ] ; then
		echo "Adding border to $img"
		convert -bordercolor "#FFFFFF" -border 20 -bordercolor "#AAAAAA" -border 3 -bordercolor "#FFFFFF" -border 40 images/$img images-border/$img
	fi
done

make html

make latex

cd _build/latex

make

# _build/latex/Lumina.tex
