import os

"""
Default settings for development environmet.

To use this settings, add the folowing line to the top of lumina_local_settings.py:

    from lumina.settings_dev import *  # noqa

"""

# ===== Lumina =====

# Dump object with {% dump_objects %}
LUMINA_DUMP_OBJECTS = True


# ===== Crispy Forms =====

CRISPY_FAIL_SILENTLY = False


# ===== Django =====

DEBUG = True

MEDIA_ROOT = os.path.expanduser('~/lumina/uploads/')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.expanduser('~/lumina.sqlite'),
    }
}

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

DEFAULT_FILE_STORAGE = 'lumina.django_files_storage.TestImagesFallbackStorage'

# Email Test Server: python -m smtpd -n -c DebuggingServer localhost:1025
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

if os.environ.get("LUMINA_TEST_SKIP_MIGRATIONS", "0") == "1":
    NOT_USED = "lumina_migrations_not_used_in_tests"
    MIGRATION_MODULES = {"lumina": NOT_USED,
                         "contenttypes": NOT_USED,
                         "admin": NOT_USED,
                         "auth": NOT_USED,
                         "sessions": NOT_USED,
                         }
