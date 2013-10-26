# -*- coding: utf-8 -*-

import logging
import pygal
import random
import pprint

from collections import defaultdict

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.exceptions import SuspiciousOperation
from django.db import connection

logger = logging.getLogger(__name__)


@login_required
@cache_control(private=True)
def view_report(request, report_id):
    assert request.user.is_photographer()
    report_id = int(report_id)
    ctx = {}
    if report_id == 1:
        ctx['report_title'] = 'Costo (hs) vs Monto cobtrado ($) por tipo de cliente'
        chart = pygal.XY(# @UndefinedVariable
            stroke=False, legend_at_bottom=True, x_title="Horas", y_title="$")
        chart.title = ctx['report_title']

        cursor = connection.cursor()
        cursor.execute("SELECT ls.session_type_id,"
            " lst.name AS \"session_type_name\","
            " ls.worked_hours AS \"worked_hours\","
            " lsq.cost AS \"orig_cost\","
            " lsqa.cost AS \"selected_quote_alternative_cost\""
            " FROM lumina_session AS ls JOIN lumina_sessionquote AS lsq ON lsq.session_id = ls.id"
            " JOIN lumina_sessiontype AS lst ON ls.session_type_id = lst.id"
            " LEFT OUTER JOIN lumina_sessionquotealternative AS lsqa"
            " ON lsq.accepted_quote_alternative_id = lsqa.id"
            " WHERE ls.worked_hours > 0 AND ls.studio_id = %s", [request.user.studio.id])
        desc = cursor.description
        values_as_dict = [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

        group_by_session_type = defaultdict(list)
        for item in values_as_dict:
            group_by_session_type[item['session_type_name']].append(item)

        logger.info("group_by_session_type: %s", pprint.pformat(group_by_session_type))

        for a_session_type, items in group_by_session_type.iteritems():
            values = [[0,0]] # HACK! without this, charts with 1 value doesn't show up
            for item in items:
                # (horas, costo)
                hours = float(item['worked_hours'])
                cost = item['selected_quote_alternative_cost'] or item['orig_cost']
                cost = float(cost)
                values.append([hours, cost])
                logger.info(" - value: %s, %s", hours, cost)
            logger.info(" - Adding new serie %s with %s values", a_session_type, len(values))
            chart.add(a_session_type, values)

        chart.print_values = False
        ctx['svg_chart'] = chart.render()
        ctx['show_form_1'] = True

    elif report_id == 2:
        ctx['report_title'] = 'Presupuestos expandidos (en el tiempo)'
        chart = pygal.StackedBar(legend_at_bottom=True, y_title="$")  #@UndefinedVariable
        chart.title = ctx['report_title']
        chart.x_labels = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', ]
        chart.add('Presupuesto original', [random.randint(17000, 25000) for _ in range(0, 6)])
        chart.add('Presupuesto expandido', [random.randint(1000, 5000) for _ in range(0, 6)])
        chart.print_values = False
        ctx['svg_chart'] = chart.render()
        ctx['show_form_2'] = True

    elif report_id == 3:
        ctx['report_title'] = 'Presupuestos expandidos (por cliente)'
        chart = pygal.StackedBar(legend_at_bottom=True, y_title="$")  #@UndefinedVariable
        chart.title = ctx['report_title']
        chart.x_labels = ['Cliente A', 'Cliente B', 'Cliente C', 'Cliente D', 'Cliente E', 'Cliente F', 'Cliente G', 'Cliente H', 'Cliente I',]
        chart.add('Presupuesto original', [random.randint(17000, 25000) for _ in range(0, 9)])
        chart.add('Presupuesto expandido', [random.randint(1000, 5000) for _ in range(0, 9)])
        chart.print_values = False
        ctx['svg_chart'] = chart.render()
        ctx['show_form_3'] = True

    elif report_id == 4:
        ctx['report_title'] = 'Ingresos ($) por tipo de cliente'
        chart = pygal.Pie(legend_at_bottom=True)  #@UndefinedVariable
        chart.title = ctx['report_title']
        chart.add('Particular (eventos)', random.randint(9000, 20000))
        chart.add('Particular (otros)', random.randint(2000, 8000))
        chart.add('Agencia de publicidad', random.randint(30000, 99000))
        chart.print_values = True
        ctx['svg_chart'] = chart.render()
        ctx['show_form_4'] = True

    else:
        raise(SuspiciousOperation())

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))
