#!/bin/sh

cd $(dirname $0)

echo ""
echo "Checking pep8..."
echo ""

pep8 --config=.pep8 --show-source --statistics lumina
EXIT_STATUS=$?
if [ "$EXIT_STATUS" -ne 0 ] ; then
	echo ""
	echo "ERROR:"
	echo ""
	echo " pep8 failed"
	echo ""
	exit $EXIT_STATUS
fi

echo ""
echo "Checking flake8... (flake8 doesn't cancels commits right now)"
echo ""

flake8 --config=.flake8 lumina

if [ "$PRE_COMMIT" != "1" ] ; then

	echo ""
	echo "Running test cases..."
	echo ""
	env RUN_SELENIUM=${RUN_SELENIUM:-0} python manage.py test --liveserver=localhost:8082 -v 2 lumina
	EXIT_STATUS=$?
	if [ "$EXIT_STATUS" -ne 0 ] ; then
		echo ""
		echo "ERROR:"
		echo ""
		echo " Test failed"
		echo ""
		exit $EXIT_STATUS
	fi

fi

