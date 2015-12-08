# -*- coding: utf-8 -*-

import logging

from django import template
from django.core.urlresolvers import reverse

from lumina import models
from lumina.pil_utils import get_image_size

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter(name='non_empty_unicode_keys')
def non_empty_unicode_keys(a_dict):
    return [str(k) for k in list(a_dict.keys()) if a_dict[k]]


@register.filter(name='full_name_with_username')
def full_name_with_username(user):
    if not user:
        return ''

    return "{0} ({1})".format(user.get_full_name(), user.username)


# ===============================================================================
# Session quote status
# ===============================================================================

@register.inclusion_tag('lumina/templatetags/session_quote_status.html')
def session_quote_status(session_quote):
    return {
        'object': session_quote,
    }


# ===============================================================================
# Thumbnails for images
# ===============================================================================

@register.inclusion_tag('lumina/templatetags/image_selection_item.html', takes_context=True)
def image_selection_item(context, image_selection, image):
    """
    Generate an item in a list of images of an 'image selection'.

    :param context: template context
    :param image_selection: the ImageSelection instance
    :param image: the Image instance
    :return:
    """
    assert isinstance(image_selection, models.ImageSelection)
    assert isinstance(image, models.Image)

    user = context['user']
    assert isinstance(user, models.LuminaUser)

    try:
        selected_images = context['LUMINA_CACHE_selected_images']
    except KeyError:
        selected_images = image_selection.selected_images.all()
        context['LUMINA_CACHE_selected_images'] = selected_images

    if image.image:
        full_quality = True
    else:
        full_quality = False

    image_filename = image.original_filename or image.thumbnail_original_filename

    thumbnail_url = reverse('image_selection_thumbnail', args=[image_selection.id, image.id])

    if user.is_for_customer():
        for_customer = True
    else:
        for_customer = False

    if image_selection.status == models.ImageSelection.STATUS_WAITING:
        waiting_selection = True
    else:
        waiting_selection = False

    return {
        'image': image,
        'image_filename': image_filename,
        'thumbnail_url': thumbnail_url,
        'for_customer': for_customer,
        'waiting_selection': waiting_selection,
        'image_selected_by_customer': image in selected_images,
        'full_quality': full_quality,
    }


@register.inclusion_tag('lumina/templatetags/image_item.html', takes_context=True)
def image_item(context, image, show_set_as_album_icon_button=False):
    """
    Generate an item in a list of images (as part of search result or images of a session).

    :param context: template context
    :param image: the Image instance
    :return:
    """
    assert isinstance(image, models.Image)

    user = context['user']
    assert isinstance(user, models.LuminaUser)
    assert user.is_photographer()

    return {
        'image': image,
        'image_filename': image.get_original_filename_or_thumbnail_original_filename(),
        'thumbnail_url': image.get_thumb_200x200_url(),
        'full_quality': image.full_quality_available(),
        'show_set_as_album_icon_button': show_set_as_album_icon_button and user.is_photographer(),
    }


@register.inclusion_tag('lumina/templatetags/gallery_image_item.js', takes_context=True)
def gallery_image_item(context, image):
    assert isinstance(image, models.Image)

    user = context['user']
    assert isinstance(user, models.LuminaUser)
    assert user.is_photographer()

    image_file = image.get_image_or_thumbnail_file()
    image_width, image_height = get_image_size(image_file)

    return {
        'image_url': reverse('get_image_or_thumb', args=[image.id]),
        'image_w': str(image_width),
        'image_h': str(image_height),
    }
