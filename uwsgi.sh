#!/bin/bash

BASEDIR=$( cd $(dirname $0) ; pwd)

if [ -z "$VIRTUAL_ENV" -a -d $BASEDIR/virtualenv ] ; then
        . $BASEDIR/virtualenv/bin/activate
fi

uwsgi --module=lumina.wsgi:application \
	--env DJANGO_SETTINGS_MODULE=lumina.settings \
	--master --processes=1 --enable-threads \
	--home=${VIRTUAL_ENV} --http=127.0.0.1:8079 \
	--python-path=${BASEDIR} --static-map /static=${BASEDIR}/lumina/static
