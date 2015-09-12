# -*- coding: utf-8 -*-

from django import forms

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout


class GenericCreateUpdateModelForm(forms.ModelForm):

    FORM_TITLE = None
    SUBMIT_LABEL = None
    CANCEL_URL = None
    FIELDS = []

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

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                self.FORM_TITLE,
                *self.FIELDS
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', self.SUBMIT_LABEL, css_id='form-submit-button'),
                layout.HTML("<a class='btn btn-primary' href='{}'>Cancelar</a>".format(self.get_cancel_url())),
            ),
        )