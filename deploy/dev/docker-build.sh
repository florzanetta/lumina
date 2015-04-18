#!/bin/bash

THISDIR=$(cd $(dirname $0); pwd)

cd $THISDIR
docker build -t lumina/dev .
