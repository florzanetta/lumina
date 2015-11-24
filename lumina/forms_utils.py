# -*- coding: utf-8 -*-

import logging

from django import forms

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout


logger = logging.getLogger(__name__)


def DatePickerField(field_name, *args, **kwargs):
    assert 'css_class' not in kwargs
    return bootstrap.PrependedText(field_name,
                                   '<i class="fa fa-calendar"></i>',
                                   css_class='force-datepicker',
                                   *args,
                                   **kwargs)
    # return layout.Field(css_class='force-datepicker', *args, **kwargs)


class _DynamicCrispyFormFields:
    def _get_crispy_form_field(self, field):
        """
        Since we no longer see uses for `get_crispy_form_field_for_X()`, the
        implementation was commented. This is a dummy implementation
        """
        if isinstance(field, layout.LayoutObject):
            return field
        assert isinstance(field, str)
        method_obj = getattr(self, "get_crispy_form_field_for_{}".format(field), None)
        assert method_obj is None
        return field

#     def _get_crispy_form_field(self, field):
#         """Returns an item for a Crispy Form field (str or instance).
#         If the method `get_crispy_form_field_for_XXX()` is found, it's used,
#         and it MUST RETURN A FIELD INSTANCE (not a str).
#
#         This exist to allow customizing a field, for example:
#
#             class SessionQuoteCreateForm(Xxxx):
#
#                 def get_crispy_form_field_for_cost(self):
#                     return bootstrap.PrependedText('cost', '$')
#
#                 FIELDS = [
#                     ···, 'cost', ···
#                 ]
#
#         """
#
#         if isinstance(field, layout.LayoutObject):
#             return field
#
#         assert isinstance(field, str)
#
#         method_name = "get_crispy_form_field_for_{}".format(field)
#         method_obj = getattr(self, method_name, None)
#         if method_obj:
#             try:
#                 crispy_field = method_obj()
#                 # TODO: is `layout.LayoutObject` the base class?
#                 assert isinstance(crispy_field, layout.LayoutObject)
#                 return crispy_field
#             except:
#                 logger.exception("Error detected when trying to call '%s()'", method_name)
#                 raise
#         else:
#             return field


class GenericCreateUpdateModelForm(forms.ModelForm,
                                   _DynamicCrispyFormFields):

    FORM_TITLE = None
    SUBMIT_LABEL = None
    CANCEL_URL = None
    FIELDS = []

    HELP_LINK = None

    def get_cancel_url(self):
        assert self.CANCEL_URL is not None, "form.CANCEL_URL must be set or `get_cancel_url()` overwritten"
        return self.CANCEL_URL

    def __init__(self, *args, **kwargs):
        assert self.FORM_TITLE is not None
        assert self.SUBMIT_LABEL is not None
        assert self.FIELDS

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        fields = [self._get_crispy_form_field(field_name)
                  for field_name in self.FIELDS]

        form_actions = (
            layout.Submit('submit_button', self.SUBMIT_LABEL, css_id='form-submit-button'),
            layout.HTML("<a class='btn btn-primary' href='{}'>Cancelar</a>".format(self.get_cancel_url())),
        )

        if self.HELP_LINK:
            form_actions += (
                layout.HTML("""
                    <span style="padding-left: 1em;"><a href="{0}" target="_blank"><i
                        class="fa fa-life-ring"></i> Ayuda</a></span>
                """.format(self.HELP_LINK)),
            )

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                self.FORM_TITLE,
                *fields
            ),
            bootstrap.FormActions(*form_actions),
        )


class GenericForm(forms.Form, _DynamicCrispyFormFields):
    """
    Similar to `GenericCreateUpdateModelForm`, without 'cancel' button,
    and plain Form (NOT ModelForm)

    FIXME: checkout how to refactor this. THis is almost equal to `GenericCreateUpdateModelForm`
    """

    FORM_TITLE = None
    SUBMIT_LABEL = None
    FIELDS = []

    def __init__(self, *args, **kwargs):
        assert self.FORM_TITLE is not None
        assert self.SUBMIT_LABEL is not None
        assert self.FIELDS

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        fields = [self._get_crispy_form_field(field_name)
                  for field_name in self.FIELDS]

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                self.FORM_TITLE,
                *fields
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', self.SUBMIT_LABEL, css_id='form-submit-button'),
            ),
        )
