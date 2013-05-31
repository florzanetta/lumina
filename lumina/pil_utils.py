from cStringIO import StringIO
from PIL import  Image as PilImage

from django.core.files.storage import default_storage


def generate_thumbnail(image):
    """
    Generates a thumbnail from a `models.Image`
    """
    img = PilImage.open(default_storage.path(image.image.path))
    img.thumbnail((100, 100,), PilImage.ANTIALIAS)
    output_file = StringIO()
    img.save(output_file, "JPEG")
    del img # no need to close it
    return output_file.getvalue()
