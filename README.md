lumina
======

[![Build Status of master](https://api.travis-ci.org/florzanetta/lumina.png?branch=master)](https://travis-ci.org/florzanetta/lumina)

Photography management software oriented to facilitate the exchange of photographies and images
for professional users, including photographers, photo labs, printing houses, and their customers.

We aim to achieve a system that can integrate the work that now photographers and other parties are doing manually and
help them connect in a way that simplyfies their workflow, saves time and optimizes communication.

We expect to do this by creating a web interface that users can use to interact with
their respective clients and that can adapt to their needs.

We believe this will add substancial value to the operations and represent
a differentiating factor to offer to their customers.

Virtualenv
----------

We use Python 2.7 (required by Django) and virtualenv. To generate the virtualenv,
in the root directory of the working copy, execute:

    $ virtualenv -p python2.7 virtualenv

To activate the virtualenv:

    $ . virtualenv/bin/activate

And to install the dependencies:

    $ pip install -r requirements.txt 

Setup of database
-----------------

By default, a Sqlite on '~/lumina.sqlite' will be used. To create it, run:

    $ python manage.py syncdb
    $ python manage.py migrate

To apply the migrations, run:

    $ python manage.py migrate lumina

To generate migrations automatically from model changes:

    $ python manage.py schemamigration lumina --auto


Reset of the database and uploads
---------------------------------

To reset the data (delete uploads, reset database and create an 'admin', user to login
with username 'admin' and password 'admin'):

    rm -rf ~/lumina.sqlite ~/lumina/uploads
    python manage.py syncdb --noinput
    python manage.py migrate

To add to the database some initial data (albums, images and shares), run:

    python manage.py loaddata sample/users.json sample/luminauserprofile.json sample/albums.json sample/images.json

The username/passwords to login are:

    * fotografo/fotografo (with Django superuser's permission)
    * cliente/cliente (customer of fotografo)
    * max_planck/max_planck (customer of fotografo)


Defaults settings
-----------------

    DATABASES['NAME'] = os.path.expanduser('~/lumina.sqlite')
    MEDIA_ROOT = os.path.expanduser('~/lumina/uploads/')


Testing
-------

To **execute the tests**, run:

    $ python manage.py test --liveserver=localhost:8082 lumina

or:

    $ python manage.py test --liveserver=localhost:8082 lumina -v 2

To include Selenium tests define the env variable **RUN_SELENIUM=1**:

    $ env RUN_SELENIUM=1 python manage.py test --liveserver=localhost:8082 lumina

To check **code coverage**, run:

    $ coverage run --source='.' --omit='virtualenv/*' manage.py test lumina
    $ coverage report

To generate **fixtures**, run:

    $ python manage.py dumpdata --format=json --indent=4 --natural auth.User lumina.luminauserprofile > lumina/fixtures/tests/users.json
    $ python manage.py dumpdata --format=json --indent=4 --natural lumina.Album > lumina/fixtures/tests/albums.json
    $ python manage.py dumpdata --format=json --indent=4 --natural lumina.Image > lumina/fixtures/tests/images.json
    $ python manage.py dumpdata --format=json --indent=4 --natural lumina.ImageSelection > lumina/fixtures/tests/imageselection-waiting-selection.json

(remember to execute this with a **CLEAN** database: see *Reset of the database and uploads*).

You can ignore the error `UserWarning: Couldn't import from 'lumina.local_settings': No module named local_settings`.
If you create a settings files for your environment, it won't appear anymore:

    $ touch lumina/local_settings.py


Travis-CI
---------

Travis-CI will:

1) check the source code for PEP8, which can be tested locally with:

    $ pep8 --show-source --statistics --max-line-length=100 --exclude=lumina/migrations --show-source lumina

2) run the tests, excluding Selenium tests:

    $ manage.py test lumina -v 2

The *checks.sh* shell script does that (a little more, since it runs Selenium tests):

    $ ./checks.sh


Git hooks
---------

To avoid breaking the builds, you could add a pre-commit hook that run the pep8 checks:

    $ cd .git/hooks/
    $ ln -s ../../.pre-commit-git-hook pre-commit


PyDev
-----

We use PyDev to develop Lumina. We recommend to setup the project with:

 + Project -> Properties -> Resources -> Text file encoding -> Other -> UTF-8
 + Project -> Properties -> Resources -> New text file line delimiter -> Other -> Unix

And, in general, to avoid pep8 errors:

 + Window -> Preferences -> PyDev -> Editor -> Code Style -> Code Formatter -> Spaces before a comment? -> 2 spaces


Licence
-------

    #===============================================================================
    #    lumina - Photography management software targeted to professional users to
    #        simplyfies their workflow, saves time and optimizes communication.
    #    Copyright (C) 2013 Horacio Guillermo de Oro <hgdeoro@gmail.com> and 
    #    Florencia Zanetta <florzanetta@gmail.com>
    #
    #    This program is free software: you can redistribute it and/or modify
    #    it under the terms of the GNU General Public License as published by
    #    the Free Software Foundation, either version 3 of the License, or
    #    (at your option) any later version.
    #
    #    This program is distributed in the hope that it will be useful,
    #    but WITHOUT ANY WARRANTY; without even the implied warranty of
    #    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    #    GNU General Public License for more details.
    #
    #    You should have received a copy of the GNU General Public License
    #    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    #===============================================================================
