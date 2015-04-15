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

We use Python 3.4 (required by Django) and virtualenv. To generate the virtualenv,
in the root directory of the working copy, execute:

    $ virtualenv -p python3.4 virtualenv

To activate the virtualenv:

    $ . virtualenv/bin/activate

And to install the dependencies:

    $ pip install -r requirements.txt 

Local config
------------

Create a `lumina_local_settings.py` in the root of the proyect, with the following content:

    from lumina.settings_dev import *

    SECRET_KEY = 'some-random-secret-key'


Setup of database
-----------------

By default, a Sqlite on `~/lumina.sqlite` will be used. To create it, run:

    $ python manage.py syncdb


How to create and apply database migrations
-------------------------------------------

To generate migrations automatically from model changes:

    $ python manage.py schemamigration lumina --auto


To apply the migrations, run:

    $ python manage.py migrate lumina


Reset of the database and uploads
---------------------------------

To reset the data (delete uploads, reset database and create an `admin`, user to login
with username `admin` and password `admin`):

    rm -rf ~/lumina.sqlite ~/lumina/uploads
    python manage.py syncdb --noinput
    python manage.py migrate

To add to the database some initial data (albums, images and shares), run:

    python manage.py loaddata sample/studios.json sample/customers.json sample/users.json sample/sessions.json sample/images.json sample/session-quotes.json


The username/passwords to login are:

    * fotografo1/fotografo1
    * fotografo2/fotografo2 (both for the same Studio)
    * cliente1/cliente1 (user for customer 'A' of fotografo1)
    * cliente2/cliente2 (user for customer 'B' of fotografo1)
    * cliente3/cliente3 (user for customer 'B' of fotografo1)

There are other users, used in test cases:

    * admin/admin (Django superuser)
    * juan
    * customer-ba07eb50-9fb5-4593-98
    * customer-957a6230-3eac-4ee1-a4

Defaults settings
-----------------

    DATABASES['NAME'] = os.path.expanduser('~/lumina.sqlite')
    MEDIA_ROOT = os.path.expanduser('~/lumina/uploads/')


<!--
Data for `cities_light` app
---------------------------

We are using `cities_light` to handle the customer city/state/country. To get
the full list of city/state/country from internet, you need to run:

    $ python manage.py cities_light

Clic [here](https://github.com/yourlabs/django-cities-light) for more info about `django-cities-light`.
-->


Testing
-------

To **execute the tests**, run:

    $ python manage.py test --liveserver=localhost:8082 lumina

To include Selenium tests define the env variable **RUN_SELENIUM=1**:

    $ env RUN_SELENIUM=1 python manage.py test --liveserver=localhost:8082 lumina

To check **code coverage**, run:

    $ coverage run --source='.' --omit='virtualenv/*' manage.py test lumina
    $ coverage report

To re-generate **fixtures** for testing, run:

    python manage.py dumpdata --format=json --indent=4 --natural lumina.Studio lumina.CustomerType lumina.SessionType lumina.PreviewSize > lumina/fixtures/sample/studios.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.Customer                                                         > lumina/fixtures/sample/customers.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.LuminaUser lumina.UserPreferences                                > lumina/fixtures/sample/users.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.Session                                                          > lumina/fixtures/sample/sessions.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.Image                                                            > lumina/fixtures/sample/images.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.ImageSelection                                                   > lumina/fixtures/sample/imageselection-waiting-selection.json
    python manage.py dumpdata --format=json --indent=4 --natural lumina.SessionQuote lumina.SessionQuoteAlternative                      > lumina/fixtures/sample/session-quotes.json

(remember to execute this with a **CLEAN** database: see *Reset of the database and uploads*).


Git hooks
---------

To avoid breaking the builds, you could add a pre-commit hook that run the pep8 checks:

    $ cd .git/hooks/
    $ ln -s ../../.pre-commit-git-hook pre-commit


Licence
-------

    #===============================================================================
    #    lumina - Photography management software targeted to professional users to
    #        simplyfies their workflow, saves time and optimizes communication.
    #    Copyright (C) 2013-2015 Horacio Guillermo de Oro <hgdeoro@gmail.com> and
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
