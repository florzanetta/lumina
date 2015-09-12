# -*- coding: utf-8 -*-

import logging

from django import forms

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout


logger = logging.getLogger(__name__)


class GenericCreateUpdateModelForm(forms.ModelForm):

    FORM_TITLE = None
    SUBMIT_LABEL = None
    CANCEL_URL = None
    FIELDS = []

    def get_cancel_url(self):
        assert self.CANCEL_URL is not None, "form.CANCEL_URL must be set or `get_cancel_url()` overwritten"
        return self.CANCEL_URL

    def _get_crispy_form_field(self, field_name):
        """Returns an item for a Crispy Form field (str or instance).
        If the method `get_crispy_form_field_for_XXX()` is found, it's used,
        and it MUST RETURN A FIELD INSTANCE (not a str).

        This exist to allow customizing a field, for example:

            class SessionQuoteCreateForm(GenericCreateUpdateModelForm):

                def get_crispy_form_field_for_cost(self):
                    return bootstrap.PrependedText('cost', '$')

                FIELDS = [
                    ···, 'cost', ···
                ]

        """
        method_name = "get_crispy_form_field_for_{}".format(field_name)
        method_obj = getattr(self, method_name, None)
        if method_obj:
            try:
                crispy_field = method_obj()
                # TODO: is `layout.LayoutObject` the base class?
                assert isinstance(crispy_field, layout.LayoutObject)
                return crispy_field
            except:
                logger.exception("Error detected when trying to call '%s()'", method_name)
                raise
        else:
            return field_name

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
                layout.HTML("<a class='btn btn-primary' href='{}'>Cancelar</a>".format(self.get_cancel_url())),
            ),
        )
