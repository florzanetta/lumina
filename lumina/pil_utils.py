import os

from io import BytesIO
from PIL import Image as PilImage
from PIL import ImageFont
from PIL import ImageDraw


from django.core.files.storage import default_storage


FONT = os.path.join(os.path.normpath(os.path.abspath(os.path.dirname(__file__))),
                    'Roboto-Black.ttf')
assert os.path.exists(FONT), "Font file not found"


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

    image_width, image_height = img.size
    max_text_size = min(image_width, max_size)

    text = image.studio.name
    font_size = 10
    watermark_font = ImageFont.truetype(FONT, font_size)
    watermark_text_width, watermark_text_height = watermark_font.getsize(text)
    while watermark_text_width < (max_text_size * 0.9):
        font_size += 2
        watermark_font = ImageFont.truetype(FONT, font_size)
        watermark_text_width, watermark_text_height = watermark_font.getsize(text)

    draw = ImageDraw.Draw(img, 'RGBA')
    pos_x = int((image_width - watermark_text_width) / 2)
    pos_y = int(((image_height - watermark_text_height) / 2))

    draw.text([pos_x, pos_y - watermark_text_height], text, font=watermark_font)
    draw.text([pos_x, pos_y + watermark_text_height], text, font=watermark_font)

    output_file = BytesIO()
    img.save(output_file, "JPEG")
    del img  # no need to close it
    return output_file.getvalue()
