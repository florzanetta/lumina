#!/usr/bin/env python
import os
import sys
import warnings

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lumina.settings")

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import autocomplete_light
        from crispy_forms import utils
        from crispy_forms.templatetags import crispy_forms_filters
        from crispy_forms.templatetags import crispy_forms_tags

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
