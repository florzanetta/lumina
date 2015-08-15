#!/bin/bash

BASEDIR=$( cd $(dirname $0) ; pwd)/../..
BASEDIR=$(realpath $BASEDIR)

if [ -L ${BASEDIR}/virtualenv-mail ] ; then
        source $(readlink ${BASEDIR}/virtualenv-mail)/bin/activate
else
        source ${BASEDIR}/virtualenv-mail/bin/activate
fi

USERS=""
for num in $(seq 9) ; do
	USERS="$USERS --user=fotografo${num}=fotografo${num} --user=cliente${num}=cliente${num}"
done

twistd \
	-n mail \
	-d lumina-photo.com.ar=${BASEDIR}/deploy/dev/mailboxes-lumina.com.ar \
	--user=notifications=notifications \
	$USERS
