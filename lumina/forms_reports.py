# -*- coding: utf-8 -*-

import logging

from django import forms

from lumina import forms_utils

logger = logging.getLogger(__name__)


class CostVsChargedByCustomerReportForm(forms_utils.GenericForm):
    FORM_TITLE = 'Parámetros del reporte'
    SUBMIT_LABEL = 'Actualizar reporte'
    FIELDS = [
        'fecha_desde', 'fecha_hasta',
    ]

    fecha_desde = forms.DateField(required=False, label='Fecha desde')
    fecha_hasta = forms.DateField(required=False, label='Fecha hasta')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_cost_vs_charged_by_customer_type'


class ExtendedQuotesThroughTimeReportForm(forms_utils.GenericForm):
    FORM_TITLE = 'Parámetros del reporte'
    SUBMIT_LABEL = 'Actualizar reporte'
    FIELDS = [
        'fecha_desde', 'fecha_hasta',
    ]

    fecha_desde = forms.DateField(required=False, label='Fecha desde')
    fecha_hasta = forms.DateField(required=False, label='Fecha hasta')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.form_action = 'report_extended_quotes_through_time'

# report_extended_quotes_by_customer

# report_income_by_customer_type
