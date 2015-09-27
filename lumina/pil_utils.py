import os

from io import BytesIO
from PIL import Image as PilImage
from PIL import ImageFont
from PIL import ImageDraw
from PIL import ImageEnhance


from django.core.files.storage import default_storage


FONT = os.path.join(os.path.normpath(os.path.abspath(os.path.dirname(__file__))),
                    'Roboto-Black.ttf')
assert os.path.exists(FONT), "Font file not found"


def _get_font(font_size):
    """Returns the font for the specified size.

    This method may fail if PIL / Pillow isn't setup correctly
    """
    return ImageFont.truetype(FONT, font_size)


def _get_font_for_image(pil_img, text, max_thumb_size):
    """Return the font with the required size so the text fits the image"""
    initial_font_size = 10
    font_size_increment = 2

    image_width, image_height = pil_img.size
    max_text_size = min(image_width, max_thumb_size)

    font_size = initial_font_size
    watermark_font = _get_font(font_size)
    watermark_text_width, watermark_text_height = watermark_font.getsize(text)
    while watermark_text_width < (max_text_size * 0.8):
        font_size += font_size_increment
        watermark_font = _get_font(font_size)
        watermark_text_width, watermark_text_height = watermark_font.getsize(text)

    return watermark_font, watermark_text_width, watermark_text_height


def generate_thumbnail(image, max_size=None, add_watermark=False):
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

    if add_watermark:
        angle = 20
        opacity = 0.8

        image_width, image_height = img.size
        text = image.studio.watermark_text or image.studio.name
        watermark_font, watermark_text_width, watermark_text_height = _get_font_for_image(img, text, max_size)

        watermark = PilImage.new('RGBA', img.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(watermark, 'RGBA')
        pos_x = int((image_width - watermark_text_width) / 2)
        pos_y = int(((image_height - watermark_text_height) / 2))

        draw.text([pos_x, pos_y - watermark_text_height], text, font=watermark_font)
        draw.text([pos_x, pos_y + watermark_text_height], text, font=watermark_font)

        watermark = watermark.rotate(angle, PilImage.BICUBIC)
        alpha = watermark.split()[3]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark.putalpha(alpha)

        PilImage.composite(watermark, img, watermark).save(output_file, 'JPEG')
    else:
        img.save(output_file, "JPEG")

    del img  # no need to close it
    return output_file.getvalue()


def get_image_size(image_file_object):
    """
    Returns size (image_width, image_height) of the image.

    `image_file_object` is a Django File object, NOT a lumina.models.Image.

    :param image_file_object:
    :return:
    """
    assert image_file_object is not None
    assert image_file_object.path

    img = PilImage.open(default_storage.path(image_file_object.path))
    image_width, image_height = img.size
    return image_width, image_height
