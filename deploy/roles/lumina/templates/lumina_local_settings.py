# -*- coding: utf-8 -*-

#
#
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
#
#
#              uuuuuuuuuuuuuuuuuuuu
#            u" uuuuuuuuuuuuuuuuuu "u
#          u" u$$$$$$$$$$$$$$$$$$$$u "u
#        u" u$$$$$$$$$$$$$$$$$$$$$$$$u "u
#      u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u
#    u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u
#  u" u$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$u "u
#  $ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $
#  $ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $
#  $ $$$" ... "$...  ...$" ... "$$$  ... "$$$ $
#  $ $$$u `"$$$$$$$  $$$  $$$$$  $$  $$$  $$$ $
#  $ $$$$$$u  "$$$$  $$$  $$$$$  $$  """ u$$$ $
#  $ $$$""$$$  $$$$  $$$u "$$$" u$$  $$$$$$$$ $
#  $ $$$$....,$$$$$..$$$$$....,$$$$..$$$$$$$$ $
#  $ $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ $
#  "u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u"
#    "u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u"
#      "u "$$$$$$$$$$$$$$$$$$$$$$$$$$$$" u"
#        "u "$$$$$$$$$$$$$$$$$$$$$$$$" u"
#          "u "$$$$$$$$$$$$$$$$$$$$" u"
#            "u """""""""""""""""" u"
#              """"""""""""""""""""
#
#
# Este archivo es autogenerado con cada deploy.
# Cualquier modificacion que se realice aqui sera
#  sobreescrita sin mayores advertencias que las presentes
#
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
# WARNING!!! ATENCION!!! WAARSCHUWING!!! WARNUNG!!! AVIS!!!
#

import os

# ==============================================================================
# Lumina
# ==============================================================================

LUMINA_DUMP_OBJECTS = True


# ==============================================================================
# Crispy Forms
# ==============================================================================

CRISPY_FAIL_SILENTLY = False


# ==============================================================================
# Django
# ==============================================================================

DEBUG = False
TEMPLATE_DEBUG = False

SECRET_KEY = '{{django_SECRET_KEY}}'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '{{django_DATABASE_NAME}}',
        'USER': '{{django_DATABASE_USER}}',
        'PASSWORD': '{{django_DATABASE_PASSWORD}}',
        'CONN_MAX_AGE': 300,
        'ATOMIC_REQUESTS': True,
    }
}

MEDIA_ROOT = '/home/lumina/deploy/media'
STATIC_ROOT = '/home/lumina/deploy/static'

ALLOWED_HOSTS = [
    "*",
]
