'''
Created on Jun 2, 2013

@author: Horacio G. de Oro
'''
import json
import logging

from django import template
from django.core import serializers
from django.db.models.query import QuerySet
from django.template.context import Context
from django.conf import settings

from lumina.models import LuminaUserProfile


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
            except AttributeError, ae:
                if ae.args[0].endswith("object has no attribute '_meta'"):
                    try:
                        objects[var_name] = json.dumps([var])
                    except TypeError, te:
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
    return [unicode(k) for k in a_dict.keys() if a_dict[k]]


@register.filter(name='user_is_customer')
def user_is_customer(user):
    if user is None:
        return False

    try:
        profile = user.luminauserprofile
        if profile.user_type == LuminaUserProfile.GUEST:
            return True
        else:
            return False
    except LuminaUserProfile.DoesNotExist:
        # If Profile doens't exists, assume is a photographer...
        return False


@register.filter(name='user_is_photographer')
def user_is_photographer(user):
    if user is None:
        return False

    try:
        profile = user.luminauserprofile
        if profile.user_type == LuminaUserProfile.PHOTOGRAPHER:
            return True
        else:
            return False
    except LuminaUserProfile.DoesNotExist:
        # If Profile doens't exists, assume is a photographer...
        return True


@register.filter(name='full_name_with_username')
def full_name_with_username(user):
    if user is None:
        return u''

    return u"{0} ({1})".format(user.get_full_name(),
                               user.username)
