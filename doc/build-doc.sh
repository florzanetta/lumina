#!/bin/bash

set -e
set -u

cd $(dirname $0)

make html

make latex

cd _build/latex

make

# _build/latex/Lumina.tex
