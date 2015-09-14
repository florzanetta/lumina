# -*- coding: utf-8 -*-

import logging

from django import forms

from lumina import forms_utils

logger = logging.getLogger(__name__)


class _GenericDateRangeReportForm(forms_utils.GenericForm):
    SUBMIT_LABEL = 'Actualizar reporte'
    FIELDS = [
        'date_from', 'date_to',
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


class CostVsChargedByCustomerReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Costo (hs) vs Monto cobrado ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + []
    FORM_ACTION = 'report_cost_vs_charged_by_customer_type'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ExtendedQuotesThroughTimeReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Presupuestos expandidos (en el tiempo)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_extended_quotes_through_time'

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class ExtendedQuotesByCustomerReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Presupuestos expandidos (por cliente)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_extended_quotes_by_customer'

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class IncomeByCustomerTypeReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Ingresos ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']
    FORM_ACTION = 'report_income_by_customer_type'

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
