#!/bin/bash

export PYTHONPATH=$PYTHONPATH:/home/lumina/deploy/src:/home/lumina/deploy/src-other:/home/lumina/deploy/local

/home/lumina/deploy/virtualenv/bin/python \
    /home/lumina/deploy/src-other/manage.py $*
