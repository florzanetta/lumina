#!/bin/bash

BASEDIR=$( cd $(dirname $0) ; pwd)/../..
BASEDIR=$(realpath $BASEDIR)

if [ -L ${BASEDIR}/virtualenv-mail ] ; then
        source $(readlink ${BASEDIR}/virtualenv-mail)/bin/activate
else
        source ${BASEDIR}/virtualenv-mail/bin/activate
fi

twistd \
	-n mail \
	-d lumina.com.ar=${BASEDIR}/deploy/dev/mailboxes-lumina.com.ar \
	--user=lumina=lumina \
	--user=photo1=photo1 \
	--user=photo2=photo2 \
	--user=customer1=customer1 \
	--user=customer2=customer2
