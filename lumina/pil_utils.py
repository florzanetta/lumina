from cStringIO import StringIO
from PIL import  Image as PilImage

from django.core.files.storage import default_storage


def generate_thumbnail(image, max_size=100):
    """
    Generates a thumbnail from a `models.Image`.
    Returns the bytes of the thumbnail.
    """
    assert image is not None
    assert isinstance(max_size, int)
    img = PilImage.open(default_storage.path(image.image.path))
    img.thumbnail((max_size, max_size,), PilImage.ANTIALIAS)
    output_file = StringIO()
    img.save(output_file, "JPEG")
    del img # no need to close it
    return output_file.getvalue()
