#!/bin/bash

BASEDIR=$( cd $(dirname $0) ; pwd)

if [ -z "${VIRTUAL_ENV}" -a -e ${BASEDIR}/virtualenv ] ; then
	if [ -L ${BASEDIR}/virtualenv ] ; then
		source $(readlink ${BASEDIR}/virtualenv)/bin/activate
	else
		source ${BASEDIR}/virtualenv/bin/activate
	fi
fi

python $BASEDIR/manage.py collectstatic --noinput

HTTP_PORT=8079
echo ""
echo "HTTP: http://127.0.0.1:$HTTP_PORT/"
echo ""

uwsgi \
	--module=lumina.wsgi:application \
	--env DJANGO_SETTINGS_MODULE=lumina.settings_uwsgi \
	--master \
	--processes=5 \
	--home=${VIRTUAL_ENV} \
	--http=127.0.0.1:$HTTP_PORT \
	--python-path=${BASEDIR} \
	--static-map /static=${BASEDIR}/deploy/dev/static \
	--master-fifo /tmp/.lumina-uwsgi \
	--req-logger file:/tmp/lumina-uwsgi.log \
	--attach-daemon ${BASEDIR}/deploy/dev/run_twistd_mail.sh \
	$*
