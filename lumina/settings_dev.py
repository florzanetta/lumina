import os

"""
Default settings for development environment.

To use this settings, add the following line to the top of lumina_local_settings.py:

    from lumina.settings_dev import *  # noqa

"""

# ===== Lumina =====

# Dump object with {% dump_objects %}
LUMINA_DUMP_OBJECTS = True


# ===== Crispy Forms =====

CRISPY_FAIL_SILENTLY = False


# ===== Django =====

BASEDIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))

DEBUG = True

MEDIA_ROOT = os.path.join(BASEDIR, "deploy", "dev", "media")
STATIC_ROOT = os.path.join(BASEDIR, "deploy", "dev", "static")

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASEDIR, "lumina.sqlite"),
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
