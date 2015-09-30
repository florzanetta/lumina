# -*- coding: utf-8 -*-

import logging
import pygal
import pprint

from collections import defaultdict

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.db import connection

from lumina import forms_reports

logger = logging.getLogger(__name__)

# FIXME: for all SQLs, check that works on PostgreSql!


@login_required
@cache_control(private=True)
def view_report_cost_vs_charged_by_customer_type(request):
    assert request.user.is_photographer()

    if request.method == 'GET':
        form = forms_reports.CostVsChargedByCustomerReportForm(user=request.user)
    else:
        form = forms_reports.CostVsChargedByCustomerReportForm(request.POST,
                                                               user=request.user)

    ctx = dict(form=form)

    ctx['report_title'] = 'Costo (hs) vs Monto cobrado ($) por tipo de cliente'
    chart = pygal.XY(  # @UndefinedVariable
                       stroke=False, legend_at_bottom=True, x_title="Horas", y_title="$")
    chart.title = ctx['report_title']

    cursor = connection.cursor()
    # FIXME: use only accepted quotes! (not canceled, or rejected by customer)
    cursor.execute(
        "SELECT ls.session_type_id,"
        " lst.name AS \"session_type_name\","
        " ls.worked_hours AS \"worked_hours\","
        " lsq.cost AS \"orig_cost\","
        " lsqa.cost AS \"selected_quote_alternative_cost\""
        " FROM lumina_session AS ls "
        " JOIN lumina_sessionquote AS lsq ON lsq.session_id = ls.id"
        " JOIN lumina_sessiontype AS lst ON ls.session_type_id = lst.id"
        " LEFT OUTER JOIN lumina_sessionquotealternative AS lsqa"
        "    ON lsq.accepted_quote_alternative_id = lsqa.id"
        " WHERE ls.worked_hours > 0 AND ls.studio_id = %s", [request.user.studio.id])
    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in cursor.fetchall()
    ]

    group_by_session_type = defaultdict(list)
    for item in values_as_dict:
        group_by_session_type[item['session_type_name']].append(item)

    logger.info("group_by_session_type: %s", pprint.pformat(group_by_session_type))

    for a_session_type, items in list(group_by_session_type.items()):
        values = [[0, 0]]  # HACK! without this, charts with 1 value doesn't show up
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

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_extended_quotes_through_time(request):
    assert request.user.is_photographer()

    if request.method == 'GET':
        form = forms_reports.ExtendedQuotesThroughTimeReportForm(user=request.user)
    else:
        form = forms_reports.ExtendedQuotesThroughTimeReportForm(request.POST,
                                                                 user=request.user)

    ctx = dict(form=form)

    ctx['report_title'] = 'Presupuestos expandidos (en el tiempo)'
    chart = pygal.StackedBar(legend_at_bottom=True, y_title="$", x_label_rotation=20)  # @UndefinedVariable
    chart.title = ctx['report_title']

    cursor = connection.cursor()
    # FIXME: use only accepted quotes! (not canceled, or rejected by customer)
    cursor.execute(
        "SELECT "
        " lsq.created AS \"date_for_report\","
        " lsq.cost AS \"orig_cost\","
        " lsqa.cost AS \"selected_quote_alternative_cost\","
        " c.name AS \"customer\""
        " FROM lumina_session AS ls"
        " JOIN lumina_sessionquote AS lsq ON lsq.session_id = ls.id"
        " JOIN lumina_customer AS c ON ls.customer_id = c.id"
        " LEFT OUTER JOIN lumina_sessionquotealternative AS lsqa"
        "    ON lsq.accepted_quote_alternative_id = lsqa.id"
        " WHERE ls.studio_id = %s", [request.user.studio.id])
    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in cursor.fetchall()
    ]

    # pprint.pprint(values_as_dict)

    group_by_date = defaultdict(list)
    for item in values_as_dict:
        group_by_date[(item['date_for_report'].year,
                       item['date_for_report'].month)].append(item)
    dates = list(group_by_date.keys())
    dates.sort()

    logger.info("group_by_date: %s", pprint.pformat(group_by_date))

    serie_cost = []
    serie_alt_quote = []
    labels = []

    for year, month in dates:
        acum_cost = 0.0
        acum_alt_quote = 0.0
        for item in group_by_date[(year, month)]:
            acum_cost += float(item['orig_cost'])
            if item['selected_quote_alternative_cost']:
                acum_alt_quote += float(item['selected_quote_alternative_cost'])
        labels.append("{}/{}".format(month, year))
        serie_cost.append(acum_cost)
        serie_alt_quote.append(acum_alt_quote)

    chart.x_labels = labels
    chart.add('Presupuesto original', serie_cost)
    chart.add('Presupuesto expandido', serie_alt_quote)
    chart.print_values = False
    ctx['svg_chart'] = chart.render()
    ctx['show_form_2'] = True

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_extended_quotes_by_customer(request):
    assert request.user.is_photographer()

    if request.method == 'GET':
        form = forms_reports.ExtendedQuotesByCustomerReportForm(user=request.user)
    else:
        form = forms_reports.ExtendedQuotesByCustomerReportForm(request.POST,
                                                                user=request.user)

    ctx = dict(form=form)

    ctx['report_title'] = 'Presupuestos expandidos (por cliente)'
    chart = pygal.StackedBar(legend_at_bottom=True, y_title="$")  # @UndefinedVariable
    chart.title = ctx['report_title']

    cursor = connection.cursor()
    # FIXME: use only accepted quotes! (not canceled, or rejected by customer)
    cursor.execute(
        "SELECT "
        " lsq.created AS \"date_for_report\","
        " lsq.cost AS \"orig_cost\","
        " lsqa.cost AS \"selected_quote_alternative_cost\","
        " c.name AS \"customer\""
        " FROM lumina_session AS ls"
        " JOIN lumina_sessionquote AS lsq ON lsq.session_id = ls.id"
        " JOIN lumina_customer AS c ON ls.customer_id = c.id"
        " LEFT OUTER JOIN lumina_sessionquotealternative AS lsqa"
        "    ON lsq.accepted_quote_alternative_id = lsqa.id"
        " WHERE ls.studio_id = %s", [request.user.studio.id])
    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in cursor.fetchall()
    ]

    group_by_customer = defaultdict(list)
    for item in values_as_dict:
        group_by_customer[item['customer']].append(item)
    customers = list(group_by_customer.keys())
    customers.sort()

    logger.info("group_by_customer: %s", pprint.pformat(group_by_customer))

    serie_cost = []
    serie_alt_quote = []
    labels = []

    for customer in customers:
        acum_cost = 0.0
        acum_alt_quote = 0.0
        for item in group_by_customer[customer]:
            acum_cost += float(item['orig_cost'])
            if item['selected_quote_alternative_cost']:
                acum_alt_quote += float(item['selected_quote_alternative_cost'])
        labels.append(customer)
        serie_cost.append(acum_cost)
        serie_alt_quote.append(acum_alt_quote)

    chart.x_labels = labels
    chart.add('Presupuesto original', serie_cost)
    chart.add('Presupuesto expandido', serie_alt_quote)
    chart.print_values = False
    ctx['svg_chart'] = chart.render()
    ctx['show_form_3'] = True

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_income_by_customer_type(request):
    assert request.user.is_photographer()

    if request.method == 'GET':
        form = forms_reports.IncomeByCustomerTypeReportForm(user=request.user)
    else:
        form = forms_reports.IncomeByCustomerTypeReportForm(request.POST,
                                                            user=request.user)

    ctx = dict(form=form)

    ctx['report_title'] = 'Ingresos ($) por tipo de cliente'
    chart = pygal.Pie(legend_at_bottom=True)  # @UndefinedVariable
    chart.title = 'Ingresos ($) por tipo de cliente'

    cursor = connection.cursor()
    # FIXME: use only accepted quotes! (not canceled, or rejected by customer)
    cursor.execute("""
    SELECT
        quot.created    AS "date_for_report",
        quot.cost       AS "orig_cost",
        quot_alt.cost   AS "selected_quote_alternative_cost",
        cust_type.name         AS "customer_type"
        FROM lumina_sessionquote    AS quot
        JOIN lumina_customer        AS cust ON quot.customer_id = cust.id
        JOIN lumina_customertype    AS cust_type ON cust.customer_type_id = cust_type.id
        LEFT OUTER JOIN lumina_sessionquotealternative AS quot_alt ON quot.accepted_quote_alternative_id = quot_alt.id
        WHERE quot.studio_id = %s
        """, [request.user.studio.id])

    all_the_rows = cursor.fetchall()
    # logger.info("all_the_rows: %s", all_the_rows)

    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in all_the_rows
    ]

    group_by_customer_type = defaultdict(list)
    for item in values_as_dict:
        group_by_customer_type[item['customer_type']].append(item)
    customer_types = list(group_by_customer_type.keys())
    customer_types.sort()

    logger.info("group_by_customer: %s", pprint.pformat(group_by_customer_type))

    serie_cost = []
    serie_alt_quote = []

    for customer in customer_types:
        acum_cost = 0.0
        acum_alt_quote = 0.0
        for item in group_by_customer_type[customer]:
            acum_cost += float(item['orig_cost'])
            if item['selected_quote_alternative_cost']:
                acum_alt_quote += float(item['selected_quote_alternative_cost'])
        serie_cost.append(acum_cost)
        serie_alt_quote.append(acum_alt_quote)

        chart.add("{} ($ {})".format(customer, acum_cost + acum_alt_quote), acum_cost + acum_alt_quote)

    chart.print_values = True
    ctx['svg_chart'] = chart.render()

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))
