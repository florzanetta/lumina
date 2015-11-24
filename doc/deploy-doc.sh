#!/bin/bash

set -e
set -u

cd $(dirname $0)

rm -rf _build

./build-doc.sh

( cd _build/latex ; make )

rsync -avc _build/html ../lumina/static/lumina/doc
