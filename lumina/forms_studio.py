# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse_lazy

from lumina import forms_utils
from lumina import models


class StudioUpdateForm(forms_utils.GenericCreateUpdateModelForm):

    # ----- <GenericCreateUpdateModelForm> -----
    FORM_TITLE = 'Actualizar datos del estudio fotográfico'
    SUBMIT_LABEL = 'Guardar'
    CANCEL_URL = reverse_lazy('home')
    FIELDS = [
        'name', 'default_terms', 'watermark_text',
    ]
    # ----- </GenericCreateUpdateModelForm> -----

    class Meta:
        model = models.Studio
        fields = (
            'name', 'default_terms', 'watermark_text',
        )
