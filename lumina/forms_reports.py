# -*- coding: utf-8 -*-

import logging

from django import forms

from lumina import forms_utils
from lumina import models

logger = logging.getLogger(__name__)


class _GenericDateRangeReportForm(forms_utils.GenericForm):
    SUBMIT_LABEL = 'Actualizar reporte'
    FIELDS = [
        forms_utils.DatePickerField('date_from'),
        forms_utils.DatePickerField('date_to'),
    ]
    FORM_ACTION = None

    date_from = forms.DateField(required=False, label='Fecha desde')
    date_to = forms.DateField(required=False, label='Fecha hasta')

    def __init__(self, *args, **kwargs):
        assert self.FORM_ACTION is not None
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.helper.form_action = self.FORM_ACTION

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")

        if date_from and date_to:
            if date_from > date_to:
                msg = "Fecha desde debe ser anterior a fecha hasta"
                self.add_error('date_from', msg)
                self.add_error('date_to', msg)


class FormWithSessionTypeMixin(forms_utils.GenericForm):

    session_type = forms.ModelChoiceField(queryset=models.SessionType.objects.none(),
                                          required=False,
                                          label='Tipo de sesión',
                                          empty_label='TODOS LOS TIPOS DE SESIONES')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['session_type'].queryset = self.user.get_session_types()


# --------------------------------------------------------------------------------


class CostVsChargedByCustomerReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Costo (hs) vs Monto cobrado ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + []
    FORM_ACTION = 'report_cost_vs_charged_by_customer_type'


class ExtendedQuotesThroughTimeReportForm(_GenericDateRangeReportForm,
                                          FormWithSessionTypeMixin):
    FORM_TITLE = 'Presupuestos expandidos (en el tiempo)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_extended_quotes_through_time'


class ExtendedQuotesByCustomerReportForm(_GenericDateRangeReportForm,
                                         FormWithSessionTypeMixin):
    FORM_TITLE = 'Presupuestos expandidos (por cliente)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_extended_quotes_by_customer'


class IncomeByCustomerTypeReportForm(_GenericDateRangeReportForm,
                                     FormWithSessionTypeMixin):
    FORM_TITLE = 'Ingresos ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_income_by_customer_type'
