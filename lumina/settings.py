# Django settings for lumina project.
import os

#===============================================================================
# Notes for 'production' settings for Lumina:
#===============================================================================
#
# - LUMINA_DUMP_OBJECTS should be False
# - DEFAULT_FILE_STORAGE: TestImagesFallbackStorage should *NO* be used in prod.
#
#===============================================================================

DEBUG = True
TEMPLATE_DEBUG = DEBUG

#
# Dump object with {% dump_objects %}
#
LUMINA_DUMP_OBJECTS = True

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

# http://south.readthedocs.org/en/latest/settings.html#south-tests-migrate
SOUTH_TESTS_MIGRATE = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.expanduser('~/lumina.sqlite'),
        # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': '',
        'PASSWORD': '',
        # Empty for localhost through domain sockets or
        #'127.0.0.1' for localhost through TCP.
        'HOST': '',
        # Set to empty string for default.
        'PORT': '',
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Argentina/Cordoba'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'es-AR'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.expanduser('~/lumina/uploads/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = ''

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    #    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 't6m&zabdb8*f=5_n0nmc(5p5an8j@ipt48z&szzufxnf4v%1ha'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    #     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'lumina.middleware.LoggingMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'lumina.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'lumina.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'social_auth',
    'south',
    'lumina',
)

#
# Path to look for web driver executable
#
SELENIUM_WEBDRIVER_BIN = (
    # Ubuntu 13.04 - Package: 'chromium-chromedriver'
    '/usr/lib/chromium-browser/chromedriver',
)

# Default:
# DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
DEFAULT_FILE_STORAGE = 'lumina.django_files_storage.TestImagesFallbackStorage'

AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    #    'social_auth.backends.facebook.FacebookBackend',
    #    'social_auth.backends.google.GoogleOAuthBackend',
    #    'social_auth.backends.google.GoogleOAuth2Backend',
    #    'social_auth.backends.google.GoogleBackend',
    #    'social_auth.backends.yahoo.YahooBackend',
    #    'social_auth.backends.browserid.BrowserIDBackend',
    #    'social_auth.backends.contrib.linkedin.LinkedinBackend',
    #    'social_auth.backends.contrib.disqus.DisqusBackend',
    #    'social_auth.backends.contrib.livejournal.LiveJournalBackend',
    #    'social_auth.backends.contrib.orkut.OrkutBackend',
    #    'social_auth.backends.contrib.foursquare.FoursquareBackend',
    #    'social_auth.backends.contrib.github.GithubBackend',
    #    'social_auth.backends.contrib.vk.VKOAuth2Backend',
    #    'social_auth.backends.contrib.live.LiveBackend',
    #    'social_auth.backends.contrib.skyrock.SkyrockBackend',
    #    'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    #    'social_auth.backends.contrib.readability.ReadabilityBackend',
    #    'social_auth.backends.contrib.fedora.FedoraBackend',
    #    'social_auth.backends.OpenIDBackend',
    'django.contrib.auth.backends.ModelBackend',
)

# The URL where requests are redirected after login when the contrib.auth.login
# view gets no next parameter.
LOGIN_REDIRECT_URL = 'home'

#
# SOCIAL_AUTH_LOGIN_REDIRECT_URL
# Where to redirect after an existing user was identified
#
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'

#
# SOCIAL_AUTH_NEW_USER_REDIRECT_URL
# Where to redirect after a new user was created
#
SOCIAL_AUTH_NEW_USER_REDIRECT_URL = '/'

SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL = '/?SOCIAL_AUTH_NEW_ASSOCIATION_REDIRECT_URL'
SOCIAL_AUTH_DISCONNECT_REDIRECT_URL = '/?SOCIAL_AUTH_DISCONNECT_REDIRECT_URL'
SOCIAL_AUTH_BACKEND_ERROR_URL = '/?SOCIAL_AUTH_BACKEND_ERROR_URL'
SOCIAL_AUTH_COMPLETE_URL_NAME = 'socialauth_complete'
SOCIAL_AUTH_ASSOCIATE_URL_NAME = 'socialauth_associate_complete'
SOCIAL_AUTH_INACTIVE_USER_URL = '/?SOCIAL_AUTH_INACTIVE_USER_URL'

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler'
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

try:
    from lumina.local_settings import *  # @UnusedWildImport
except ImportError, e:
    import warnings
    warnings.warn("Couldn't import from 'lumina.local_settings': %s" % e.args[0], stacklevel=0)
    TWITTER_CONSUMER_KEY = ''
    TWITTER_CONSUMER_SECRET = ''
