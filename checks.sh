#!/bin/sh

echo ""
echo "Checking pep8..."
echo ""

pep8 --show-source --statistics --max-line-length=120 --exclude=lumina/migrations --show-source lumina
if [ "$?" -ne 0 ] ; then
	echo ""
	echo "ERROR:"
	echo ""
	echo " pep8 failed"
	echo ""
	exit 1
fi

echo ""
echo "Running test cases..."
echo ""

env RUN_SELENIUM=1 python manage.py test --liveserver=localhost:8082 -v 2 lumina
if [ "$?" -ne 0 ] ; then
	echo ""
	echo "ERROR:"
	echo ""
	echo " Test failed"
	echo ""
	exit 1
fi

echo "Ready to push..."
