'''
Created on Jun 2, 2013

@author: Horacio G. de Oro
'''
import json
import logging

from django import template
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models.query import QuerySet
from django.template.context import Context
from django.conf import settings

from lumina import models
from lumina.pil_utils import get_image_size

logger = logging.getLogger(__name__)

register = template.Library()


# https://docs.djangoproject.com/en/1.5/howto/custom-template-tags/

class DumpObjectsNode(template.Node):
    def __init__(self, object_names):
        self.template_variables = [template.Variable(obj_name) for obj_name in object_names]

    def render(self, context):
        # https://docs.djangoproject.com/en/1.5/topics/serialization/
        objects = {}
        json_to_show = []
        for t_var in self.template_variables:
            var_name = t_var.var
            json_to_show.append('')
            json_to_show.append('-' * 70)
            json_to_show.append(var_name)
            json_to_show.append('-' * 70)
            try:
                var = t_var.resolve(context)
            except template.VariableDoesNotExist:
                objects[var_name] = json.dumps([])
                continue

            try:
                if isinstance(var, QuerySet):
                    objects[var_name] = serializers.serialize('json', var, indent=2)
                else:
                    objects[var_name] = serializers.serialize('json', [var], indent=2)
            except AttributeError as ae:
                if ae.args[0].endswith("object has no attribute '_meta'"):
                    try:
                        objects[var_name] = json.dumps([var])
                    except TypeError as te:
                        if te.args[0].endswith("is not JSON serializable"):
                            objects[var_name] = str(var)
                        else:
                            raise
                else:
                    raise

            json_to_show.append(objects[var_name])
            # </end for>

        t = template.loader.get_template('lumina/templatetags/dump_objects.html')
        return t.render(Context({
            'json': json.dumps(objects),
            'json_to_show': '\n'.join(json_to_show),
            'dump_objects': settings.LUMINA_DUMP_OBJECTS,
        }))


@register.tag
def dump_objects(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        split_contents = token.split_contents()
        objects = split_contents[1:]
    except ValueError:
        raise template.TemplateSyntaxError("{0} tag requires a single argument".format(
            token.contents.split()[0]))
    return DumpObjectsNode(objects)


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

    if image.image:
        full_quality = True
    else:
        full_quality = False

    image_filename = image.original_filename or image.thumbnail_original_filename

    thumbnail_url = reverse('image_thumb_64x64', args=[image.id])
    # thumbnail_url = reverse('image_selection_thumbnail', args=[image_selection.id, image.id])

    return {
        'image': image,
        'image_filename': image_filename,
        'thumbnail_url': thumbnail_url,
        'full_quality': full_quality,
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
