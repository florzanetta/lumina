"""
WSGI config for proj project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import warnings

from django.core.wsgi import get_wsgi_application


with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from crispy_forms import utils
    from crispy_forms.templatetags import crispy_forms_filters
    from crispy_forms.templatetags import crispy_forms_tags

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumina.settings")

application = get_wsgi_application()
