lumina
======

Photography management software oriented to both labs and professional photographers.

This project is centered in the need of the photographers and labs for an integrated system to help
and facilitate the communication between them and the final customers of their work.

We aim to achieve a system that can integrate the work that now photographers and labs are doing manually and
help them connect in a way that simplyfies their workflow, saves time and optimizes communication.

We expect to do this by creating a web interface that both labs and photoghaphers can use to interact with
their respective clients and that can adapt to both their needs.

We believe this will add substancial value to the operations of labs as well as photographers and represent
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
    $ python manage.py migrate lumina


Licence
-------

    #===============================================================================
    #    lumina - Photography management software oriented to labs and photographers
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
