'''
Created on Jun 2, 2013

@author: Horacio G. de Oro
'''
import json

from django import template
from django.core import serializers
from django.db.models.query import QuerySet
from django.template.context import Context
from django.conf import settings


register = template.Library()


# https://docs.djangoproject.com/en/1.5/howto/custom-template-tags/

class DumpObjectsNode(template.Node):
    def __init__(self, object_names):
        self.template_variables = [template.Variable(obj_name) for obj_name in object_names]

    def render(self, context):
        # https://docs.djangoproject.com/en/1.5/topics/serialization/
        objects = {}
        for t_var in self.template_variables:
            var_name = t_var.var
            try:
                var = t_var.resolve(context)
            except template.VariableDoesNotExist:
                objects[var_name] = json.dumps([])
                continue

            try:
                if isinstance(var, QuerySet):
                    objects[var_name] = serializers.serialize('json', var)
                else:
                    objects[var_name] = serializers.serialize('json', [var])
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

        t = template.loader.get_template('lumina/templatetags/dump_objects.html')
        return t.render(Context({
            'json': json.dumps(objects),
            'debug': settings.DEBUG,
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
