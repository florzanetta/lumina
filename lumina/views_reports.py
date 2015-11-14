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
from lumina import models

logger = logging.getLogger(__name__)

# FIXME: for all SQLs, check that works on PostgreSql!


PYGAL_CONFIG = pygal.Config(
    js=["/static/lumina/pygal-tooltips.min.js"],
    no_data_text="Sin datos"
)


@login_required
@cache_control(private=True)
def view_report_cost_vs_charged_by_customer_type(request):
    assert request.user.is_photographer()

    ctx = {
        'report_title': 'Costo (hs) vs Monto cobrado ($) por tipo de cliente',
    }

    if request.method == 'GET':
        form = forms_reports.CostVsChargedByCustomerReportForm(user=request.user)
        ctx['form'] = form

        return render_to_response(
            'lumina/reports/report_generic.html', ctx,
            context_instance=RequestContext(request))

    else:
        form = forms_reports.CostVsChargedByCustomerReportForm(request.POST, user=request.user)
        ctx['form'] = form

        if not form.is_valid():
            return render_to_response(
                'lumina/reports/report_generic.html', ctx,
                context_instance=RequestContext(request))

    query_sql = """
    SELECT
        quot.cost             AS "orig_cost",
        quot_alt.cost         AS "selected_quote_alternative_cost",
        sess.worked_hours     AS "worked_hours",
        cust.customer_type_id AS "customer_type_id"
    FROM
        lumina_sessionquote AS quot
        JOIN lumina_customer AS cust ON quot.customer_id = cust.id
        JOIN lumina_session AS sess ON quot.session_id = sess.id
        LEFT OUTER JOIN lumina_sessionquotealternative AS quot_alt
            ON quot.accepted_quote_alternative_id = quot_alt.id
    WHERE
        quot.status = %s    AND
        quot.studio_id = %s AND
        quot.created >= %s  AND
        quot.created <= %s
    """

    query_params = [
        models.SessionQuote.STATUS_ACCEPTED,
        request.user.studio.id,
        form.cleaned_data['date_from'],
        form.cleaned_data['date_to']
    ]

    cursor = connection.cursor()
    cursor.execute(query_sql, query_params)

    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in cursor.fetchall()
    ]

    group_by_customer_type = defaultdict(list)
    for item in values_as_dict:
        group_by_customer_type[item['customer_type_id']].append(item)

    logger.info("group_by_customer_type: %s", pprint.pformat(group_by_customer_type))

    chart = pygal.XY(stroke=False,
                     legend_at_bottom=True,
                     x_title="Horas",
                     y_title="$",
                     config=PYGAL_CONFIG)
    chart.title = ctx['report_title']

    # Consider reported cutomer types, and also archived customer types that are included in the results.
    # Archived customer types NOT reported are ignored
    active_customer_types = list([ct.id for ct in request.user.get_customer_types()])
    reported_customer_types = list(group_by_customer_type.keys())
    all_customer_types_id = active_customer_types + reported_customer_types
    all_customer_types = set([
        models.CustomerType.objects.get(pk=ct_id) for ct_id in all_customer_types_id
    ])
    all_customer_types = sorted(list(all_customer_types), key=lambda ct: ct.name)

    # for a_customer_type_id, items in list(group_by_customer_type.items()):
    for a_customer_type in all_customer_types:
        items = group_by_customer_type[a_customer_type.id]
        values = []
        for item in items:
            # (horas, costo)
            hours = float(item['worked_hours'])
            cost = item['selected_quote_alternative_cost'] or item['orig_cost']
            cost = float(cost)
            values.append([hours, cost])
            logger.debug(" - value: %s, %s", hours, cost)
        logger.debug(" - Adding new serie %s with %s values", a_customer_type, len(values))
        chart.add(a_customer_type.name, values)

    chart.print_values = False
    ctx['svg_chart'] = chart.render()

    return render_to_response('lumina/reports/report_generic.html', ctx, context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_extended_quotes_by_customer(request):
    assert request.user.is_photographer()

    ctx = {
        'report_title': 'Ingresos ($) por tipo de cliente',
    }

    if request.method == 'GET':
        form = forms_reports.ExtendedQuotesByCustomerReportForm(user=request.user)
        ctx['form'] = form

        return render_to_response(
            'lumina/reports/report_generic.html', ctx,
            context_instance=RequestContext(request))

    else:
        form = forms_reports.ExtendedQuotesByCustomerReportForm(request.POST, user=request.user)
        ctx['form'] = form

        if not form.is_valid():
            return render_to_response(
                'lumina/reports/report_generic.html', ctx,
                context_instance=RequestContext(request))

    query_sql = """
    SELECT
        sess_quo.created    AS "date_for_report",
        sess_quo.cost       AS "orig_cost",
        sess_quo_alt.cost   AS "selected_quote_alternative_cost",
        cust.name           AS "customer"
    FROM
        lumina_sessionquote as sess_quo
        JOIN lumina_customer AS cust
            ON sess_quo.customer_id = cust.id
        LEFT OUTER JOIN lumina_sessionquotealternative AS sess_quo_alt
            ON sess_quo.accepted_quote_alternative_id = sess_quo_alt.id
    WHERE
        sess_quo.status = %s AND
        sess_quo.studio_id = %s AND
        sess_quo.created >= %s  AND
        sess_quo.created <= %s
    """

    query_params = [
        models.SessionQuote.STATUS_ACCEPTED,
        request.user.studio.id,
        form.cleaned_data['date_from'],
        form.cleaned_data['date_to']
    ]

    cursor = connection.cursor()
    cursor.execute(query_sql, query_params)

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

    chart = pygal.StackedBar(legend_at_bottom=True, y_title="$", config=PYGAL_CONFIG)
    chart.title = ctx['report_title']

    chart.x_labels = labels
    chart.add('Presupuesto original', serie_cost)
    chart.add('Presupuesto expandido', serie_alt_quote)
    chart.print_values = False
    ctx['svg_chart'] = chart.render()
    ctx['show_form_3'] = True

    return render_to_response('lumina/reports/report_generic.html', ctx, context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_income_by_customer_type(request):
    assert request.user.is_photographer()

    ctx = {
        'report_title': 'Ingresos ($) por tipo de cliente',
    }

    if request.method == 'GET':
        form = forms_reports.IncomeByCustomerTypeReportForm(user=request.user)
        ctx['form'] = form

        return render_to_response(
            'lumina/reports/report_generic.html', ctx,
            context_instance=RequestContext(request))

    else:
        form = forms_reports.IncomeByCustomerTypeReportForm(request.POST, user=request.user)
        ctx['form'] = form

        if not form.is_valid():
            return render_to_response(
                'lumina/reports/report_generic.html', ctx,
                context_instance=RequestContext(request))

    cursor = connection.cursor()
    cursor.execute("""
    SELECT
        cust.customer_type_id   AS "customer_type",
        quot.created    AS "date_for_report",
        quot.cost       AS "orig_cost",
        quot_alt.cost   AS "selected_quote_alternative_cost"
        FROM lumina_sessionquote    AS quot
        JOIN lumina_customer        AS cust ON quot.customer_id = cust.id
        LEFT OUTER JOIN lumina_sessionquotealternative AS quot_alt ON quot.accepted_quote_alternative_id = quot_alt.id
        WHERE
            quot.status = %s    AND
            quot.studio_id = %s AND
            quot.created >= %s  AND
            quot.created <= %s
        """, [models.SessionQuote.STATUS_ACCEPTED,
              request.user.studio.id,
              form.cleaned_data['date_from'],
              form.cleaned_data['date_to']])

    # Calculate values
    total_by_customer = defaultdict(lambda: 0.0)
    for customer_type, date_for_report, orig_cost, selected_quote_alternative_cost in cursor.fetchall():
        if selected_quote_alternative_cost:
            total_by_customer[customer_type] += float(selected_quote_alternative_cost)
        else:
            total_by_customer[customer_type] += float(orig_cost)

    # Generate chart series
    customer_type_names = dict([

        (ct.id, ct.name) for ct in models.CustomerType.objects.filter(studio=request.user.studio)
    ])

    chart = pygal.Pie(legend_at_bottom=True,
                      config=PYGAL_CONFIG)
    chart.title = 'Ingresos ($) por tipo de cliente'
    chart.print_values = True

    for customer_type in total_by_customer.keys():
        label = "{} ($ {})".format(customer_type_names[customer_type], total_by_customer[customer_type])
        chart.add(label, total_by_customer[customer_type])

    ctx['svg_chart'] = chart.render()

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))


@login_required
@cache_control(private=True)
def view_extended_quotes_through_time(request):
    assert request.user.is_photographer()

    ctx = {
        'report_title': 'Presupuestos expandidos (en el tiempo)',
    }

    if request.method == 'GET':
        form = forms_reports.ExtendedQuotesThroughTimeReportForm(user=request.user)
        ctx['form'] = form

        return render_to_response(
            'lumina/reports/report_generic.html', ctx,
            context_instance=RequestContext(request))

    else:
        form = forms_reports.ExtendedQuotesThroughTimeReportForm(request.POST, user=request.user)
        ctx['form'] = form

        if not form.is_valid():
            return render_to_response(
                'lumina/reports/report_generic.html', ctx,
                context_instance=RequestContext(request))

    query_sql = """
    SELECT
        sess_quo.created    AS "date_for_report",
        sess_quo.cost       AS "orig_cost",
        sess_quo_alt.cost   AS "selected_quote_alternative_cost",
        cust.name           AS "customer"
    FROM
        lumina_sessionquote as sess_quo
        JOIN lumina_customer AS cust
            ON sess_quo.customer_id = cust.id
        LEFT OUTER JOIN lumina_sessionquotealternative AS sess_quo_alt
            ON sess_quo.accepted_quote_alternative_id = sess_quo_alt.id
    WHERE
        sess_quo.status = %s AND
        sess_quo.studio_id = %s AND
        sess_quo.created >= %s  AND
        sess_quo.created <= %s
    """

    query_params = [
        models.SessionQuote.STATUS_ACCEPTED,
        request.user.studio.id,
        form.cleaned_data['date_from'],
        form.cleaned_data['date_to']
    ]

    cursor = connection.cursor()
    cursor.execute(query_sql, query_params)

    desc = cursor.description
    values_as_dict = [
        dict(list(zip([col[0] for col in desc], row)))
        for row in cursor.fetchall()
    ]

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

    chart = pygal.StackedBar(legend_at_bottom=True,
                             y_title="$",
                             x_label_rotation=20,
                             config=PYGAL_CONFIG)
    chart.title = ctx['report_title']

    chart.x_labels = labels
    chart.add('Presupuesto original', serie_cost)
    chart.add('Presupuesto expandido', serie_alt_quote)
    chart.print_values = False
    ctx['svg_chart'] = chart.render()
    ctx['show_form_2'] = True

    return render_to_response(
        'lumina/reports/report_generic.html', ctx,
        context_instance=RequestContext(request))
