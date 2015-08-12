from io import BytesIO
from PIL import Image as PilImage

from django.core.files.storage import default_storage


def generate_thumbnail(image, max_size=None):
    """
    Generates a thumbnail from a `models.Image`.
    If `max_size` is None, the default value is used.
    Returns the bytes of the thumbnail.
    """
    if max_size is None:
        max_size = 100
    assert image is not None
    assert isinstance(max_size, int)
    if image.thumbnail_image:
        img = PilImage.open(default_storage.path(image.thumbnail_image.path))
    else:
        img = PilImage.open(default_storage.path(image.image.path))
    img.thumbnail((max_size, max_size,), PilImage.ANTIALIAS)
    output_file = BytesIO()
    img.save(output_file, "JPEG")
    del img  # no need to close it
    return output_file.getvalue()
