#!/bin/bash

THISDIR=$(cd $(dirname $0); pwd)
cd $THISDIR

NAME=${NAME:-lumina-dev}
IMAGE=${IMAGE:-lumina/dev}
VOLUMES_ROOT=${VOLUMES_ROOT:-/srv/docker-lumina-dev}

docker run \
	--name $NAME \
        -v $VOLUMES_ROOT/var_lib_apt:/var/lib/apt \
        -v $VOLUMES_ROOT/var_cache_apt:/var/cache/apt \
        -v $VOLUMES_ROOT/home_lumina_deploy:/home/lumina/deploy \
	-p 9922:22 \
	-p 9923:5432 \
	-d \
	$IMAGE
