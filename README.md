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

Update pip and to install the dependencies:

    $ pip install -U pip
    $ pip install -r requirements.txt 

Local config
------------

Create a `lumina_local_settings.py` in the root of the project, with the following content:

    from lumina.settings_dev import *

    SECRET_KEY = 'some-random-secret-key'


Setup of database
-----------------

By default, a Sqlite on `lumina.sqlite` will be used. To create it, run:

    $ python manage.py syncdb


Testing
-------

To **execute the tests**, run:

    $ python manage.py test --liveserver=localhost:8082 lumina

To include Selenium tests define the env variable **RUN_SELENIUM=1**:

    $ env RUN_SELENIUM=1 python manage.py test --liveserver=localhost:8082 lumina

To check **code coverage**, run:

    $ coverage run --source='.' --omit='virtualenv/*' manage.py test lumina
    $ coverage report


Git hooks
---------

To avoid breaking the builds, you could add a pre-commit hook that run the pep8 checks:

    $ cd .git/hooks/
    $ ln -s ../../.pre-commit-git-hook pre-commit


Icons: attribution
------------------

Icons made by Freepik from www.flaticon.com is licensed under CC BY 3.0

GLYPHICONS from Bootstrap - http://glyphicons.com/ - Jan Kovarik

Font Awesome - Created by Dave Gandy

Licence
-------

    #===============================================================================
    #    lumina - Photography management software targeted to professional users to
    #        simplifies their workflow, saves time and optimizes communication.
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
