# -*- coding: utf-8 -*-

import logging

from django import forms

from lumina import forms_utils

logger = logging.getLogger(__name__)


class _GenericDateRangeReportForm(forms_utils.GenericForm):
    SUBMIT_LABEL = 'Actualizar reporte'
    FIELDS = [
        'fecha_desde', 'fecha_hasta',
    ]

    fecha_desde = forms.DateField(required=False, label='Fecha desde')
    fecha_hasta = forms.DateField(required=False, label='Fecha hasta')

    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get("fecha_desde")
        fecha_hasta = cleaned_data.get("fecha_hasta")

        if fecha_desde and fecha_hasta:
            if fecha_desde > fecha_hasta:
                msg = "Fecha desde debe ser anterior a fecha hasta"
                self.add_error('fecha_desde', msg)
                self.add_error('fecha_hasta', msg)


class CostVsChargedByCustomerReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Costo (hs) vs Monto cobrado ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_cost_vs_charged_by_customer_type'


class ExtendedQuotesThroughTimeReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Presupuestos expandidos (en el tiempo)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_extended_quotes_through_time'


class ExtendedQuotesByCustomerReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Presupuestos expandidos (por cliente)'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_extended_quotes_by_customer'


class IncomeByCustomerTypeReportForm(_GenericDateRangeReportForm):
    FORM_TITLE = 'Ingresos ($) por tipo de cliente'
    FIELDS = _GenericDateRangeReportForm.FIELDS + ['session_type']

    session_type = forms.ChoiceField(required=False, label='Tipo de sesión')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_income_by_customer_type'
