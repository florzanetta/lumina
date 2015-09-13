from django.core import checks

from lumina import pil_utils


@checks.register()
def example_check(app_configs, **kwargs):
    errors = []
    try:
        pil_utils._get_font(10)
    except ImportError:
        errors.append(
            checks.Error(
                'ImageFont.truetype() raised an error',
                hint="Maybe you should install libfreetype6-dev and rebuild PIL / Pillow",
                obj='',
                id='lumina.E001',
            )
        )
    return errors
