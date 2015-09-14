# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse_lazy

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout

from lumina import forms_utils
from lumina import models


class SessionQuoteCreateForm(forms_utils.GenericCreateUpdateModelForm):

    def get_crispy_form_field_for_cost(self):
        return bootstrap.PrependedText('cost', '$')

    def get_crispy_form_field_for_stipulated_down_payment(self):
        return bootstrap.PrependedText('stipulated_down_payment', '$')

    FORM_TITLE = 'Crear nuevo presupuesto'
    SUBMIT_LABEL = 'Crear'
    CANCEL_URL = reverse_lazy('quote_list')
    FIELDS = [
        'name',
        'customer',
        'image_quantity',
        forms_utils.DatePickerField('stipulated_date'),
        'cost',
        'stipulated_down_payment',
        'terms'
    ]

    class Meta:
        model = models.SessionQuote
        fields = (
            'name', 'customer', 'image_quantity', 'stipulated_date', 'cost',
            'stipulated_down_payment',
            'terms'
        )

    def clean(self):
        cleaned_data = super().clean()
        cost = cleaned_data.get("cost")
        stipulated_down_payment = cleaned_data.get("stipulated_down_payment")

        if cost is not None and stipulated_down_payment is not None:
            if cost < stipulated_down_payment:
                msg = "La 'entrega inicial pactada' debe ser menor o igual al 'costo'"
                self.add_error('cost', msg)
                self.add_error('stipulated_down_payment', msg)


class SessionQuoteUpdateForm(forms.ModelForm):

    class Meta:
        model = models.SessionQuote
        fields = ('name', 'customer', 'image_quantity', 'cost',
                  'terms')


class SessionQuoteUpdate2Form(forms.ModelForm):

    class Meta:
        model = models.SessionQuote
        fields = []


class SessionQuoteSearchForm(forms.Form):

    ARCHIVED_STATUS_ALL = 'ALL'
    ARCHIVED_STATUS_ARCHIVED = 'ARCHIVED'
    ARCHIVED_STATUS_ACTIVE = 'ACTIVE'

    ARCHIVED_STATUS_CHOICES = (
        (ARCHIVED_STATUS_ALL, 'Todas'),
        (ARCHIVED_STATUS_ARCHIVED, 'Archivadas'),
        (ARCHIVED_STATUS_ACTIVE, 'Activas'),
    )
    archived_status = forms.ChoiceField(choices=ARCHIVED_STATUS_CHOICES,
                                        widget=forms.RadioSelect,
                                        initial=ARCHIVED_STATUS_ALL,
                                        label='Archivados',
                                        required=False)

    fecha_creacion_desde = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (desde)")
    fecha_creacion_hasta = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (hasta)")
    customer = forms.ModelChoiceField(models.Customer.objects.none(),
                                      empty_label='Todos los clientes',
                                      label='Cliente',
                                      required=False)
    page = forms.CharField(max_length=5, required=False, widget=forms.HiddenInput)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = 'quote_search'
        self.helper.form_id = 'form-session-quote-search'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        assert isinstance(user, models.LuminaUser)
        if user.is_photographer():
            self.helper.layout = helper.Layout(
                bootstrap.InlineRadios('archived_status'),
                forms_utils.DatePickerField('fecha_creacion_desde'),
                forms_utils.DatePickerField('fecha_creacion_hasta'),
                'customer',
                'page',
                bootstrap.FormActions(
                    layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
                ),
            )
            self.fields['customer'].queryset = models.Customer.objects.customers_of(user)
        else:
            self.helper.layout = helper.Layout(
                forms_utils.DatePickerField('fecha_creacion_desde'),
                forms_utils.DatePickerField('fecha_creacion_hasta'),
                'page',
                bootstrap.FormActions(
                    layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
                ),
            )

    def clean(self):
        cleaned_data = super().clean()
        fecha_creacion_desde = cleaned_data.get("fecha_creacion_desde")
        fecha_creacion_hasta = cleaned_data.get("fecha_creacion_hasta")

        if fecha_creacion_desde and fecha_creacion_hasta:
            if fecha_creacion_desde > fecha_creacion_hasta:
                msg = "'Fecha de creacion (desde)' debe ser anterior a 'Fecha de creacion (hasta)'"
                self.add_error('fecha_creacion_desde', msg)
                self.add_error('fecha_creacion_hasta', msg)


class SessionQuoteAlternativeCreateForm(forms.ModelForm):

    class Meta:
        model = models.SessionQuoteAlternative
        fields = ('image_quantity', 'cost')


# ===============================================================================
# SessionQuoteAlternative
# ===============================================================================

# # inline formset + class based views -> http://haineault.com/blog/155/
#
# # from django.forms.models import BaseModelFormSet
# # class BaseSessionQuoteAlternativeFormSet(BaseModelFormSet):
# #     def __init__(self, *args, **kwargs):
# #         super(BaseSessionQuoteAlternativeFormSet, self).__init__(*args, **kwargs)
# #         self.queryset = Author.objects.filter()
# #
# # SessionQuoteAlternativeFormSet = modelformset_factory(SessionQuoteAlternative,
# #                                                       formset=BaseSessionQuoteAlternativeFormSet)
#
# # SessionQuoteAlternativeFormSet = modelformset_factory(SessionQuoteAlternative)
#
# SessionQuoteAlternativeFormSet = inlineformset_factory(SessionQuote,
#                                                        SessionQuoteAlternative,
#                                                        can_delete=True,
#                                                        extra=3)
