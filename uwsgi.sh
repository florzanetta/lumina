#!/bin/bash

BASEDIR=$( cd $(dirname $0) ; pwd)

if [ -z "$VIRTUAL_ENV" -a -d $BASEDIR/virtualenv ] ; then
        . $BASEDIR/virtualenv/bin/activate
fi

python $BASEDIR/manage.py collectstatic --noinput

HTTP_PORT=8079
echo ""
echo "HTTP: http://127.0.0.1:$HTTP_PORT/"
echo ""

uwsgi --module=lumina.wsgi:application \
	--env DJANGO_SETTINGS_MODULE=lumina.settings_uwsgi \
	--master --processes=1 --enable-threads \
	--home=${VIRTUAL_ENV} --http=127.0.0.1:$HTTP_PORT \
	--python-path=${BASEDIR} --static-map /static=${BASEDIR}/deploy/dev/static
