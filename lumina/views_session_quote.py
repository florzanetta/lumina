# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import CreateView, UpdateView, FormMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.core import paginator as django_paginator
from django.conf import settings
from django.contrib.messages.views import SuccessMessageMixin

from lumina import forms_session_quote
from lumina import views_utils

from lumina.models import SessionQuote, SessionQuoteAlternative
from lumina.mail import send_email_for_session_quote

logger = logging.getLogger(__name__)


# ===============================================================================
# SessionQuote
# ===============================================================================

class SessionQuoteCreateUpdateMixin:
    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers


class SessionQuoteCreateView(CreateView, SessionQuoteCreateUpdateMixin):
    model = SessionQuote
    form_class = forms_session_quote.SessionQuoteCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    def get_form(self, form_class):
        form = super().get_form(form_class)
        self._setup_form(form)
        form.fields['terms'].initial = self.request.user.studio.default_terms or ''
        return form

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super(SessionQuoteCreateView, self).form_valid(form)
        messages.success(self.request, 'El presupuesto fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear presupuesto"
        context['submit_label'] = "Crear"
        return context

    def get_success_url(self):
        return reverse('quote_detail', args=[self.object.id])


class SessionQuoteUpdateView(SuccessMessageMixin, UpdateView, SessionQuoteCreateUpdateMixin):
    """
    Allows the photographer modify a Quote.

    The SessionQuote instance is fully modificable ONLY if in state STATUS_QUOTING.
    If STATUS_WAITING_CUSTOMER_RESPONSE or STATUS_ACCEPTED, only the alternatives
    are modificables.

    So:
    - SessionQuote.STATUS_QUOTING => fully editable
    - SessionQuote.STATUS_ACCEPTED => only SessionQuoteAlternative are editable
    - SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE => only SessionQuoteAlternative are editable
    """
    model = SessionQuote
    template_name = 'lumina/sessionquote_update_form.html'
    success_message = "El presupuesto fue actualizado exitosamente"

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['photographer'] = self.request.user
        return form_kwargs

    def get_form_class(self):
        if self.object.status == SessionQuote.STATUS_QUOTING:  # fully editable
            return forms_session_quote.SessionQuoteUpdateForm

        elif self.object.status in [SessionQuote.STATUS_ACCEPTED,  # only SessionQuoteAlternative are editable
                                    SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE]:
            return forms_session_quote.SessionQuoteUpdateEmptyForm

        else:
            raise SuspiciousOperation()

    def get_queryset(self):
        return SessionQuote.objects.modificable_sessionquote(self.request.user)

    def form_valid(self, form):

        # Update the `SessionQuote`
        if self.object.status == SessionQuote.STATUS_QUOTING:
            if 'submit_update_quote' in self.request.POST:  # Submit for 'Update'
                return super().form_valid(form)

        # Check if post was for alternative management
        delete_alternative = [k for k in list(self.request.POST.keys())
                              if k.startswith('delete_alternative_')]

        if delete_alternative:
            assert len(delete_alternative) == 1
            alt_to_delete = delete_alternative[0].split('_')[2]
            to_delete = self.object.quote_alternatives.get(pk=int(alt_to_delete))
            to_delete.delete()
            # This delete is super-safe because the foreign-key is set to 'PROTECT'.
            # If the customer changes his/her alternative to the one being deleted,
            # the DB will refuse this delete automatically :-D
            return HttpResponseRedirect(reverse('quote_update', args=[self.object.id]))

        # TODO: add an error messages and do a redirect instead of this?
        raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.object.status == SessionQuote.STATUS_QUOTING:
            context['full_edit'] = True
        else:
            context['full_edit'] = False

        views_utils.put_session_statuses_in_context(context)
        return context

    def get_success_url(self):
        return reverse('quote_detail', args=[self.object.id])


class SessionQuoteListView(ListView):
    """
    List all the NON-archived quotes (only usefull for photographers)
    """
    model = SessionQuote

    def get_queryset(self):
        assert self.request.user.is_photographer()
        qs = SessionQuote.objects.visible_sessionquote(self.request.user)
        qs = qs.filter(archived=False)
        return qs.order_by('customer__name', 'id')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            show_add_session_button=True,
            **kwargs)


class SessionQuotePendigForCustomerListView(SessionQuoteListView):

    def get_queryset(self):
        qs = SessionQuote.objects.visible_sessionquote(self.request.user)
        qs = qs.filter(status=SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)
        return qs.order_by('customer__name', 'id')

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            custom_title="Listado de presupuestos pendientes de aceptar",
            hide_customer=True,
            **kwargs)


class SessionQuoteSearchView(ListView, FormMixin):
    model = SessionQuote
    template_name = ''

    PAGE_RESULT_SIZE = settings.LUMINA_DEFAULT_PAGINATION_SIZE

    def get_queryset(self):
        return SessionQuote.objects.none()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=forms_session_quote.SessionQuoteSearchForm)
        self.search_result_qs = None

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=forms_session_quote.SessionQuoteSearchForm)
        self.search_result_qs = self._do_search(request, self.form)

        return super().get(request, *args, **kwargs)

    def _do_search(self, request, form):
        """Returns QuerySet"""
        # Validate form
        if not form.is_valid():
            messages.error(request,
                           "Los parámetros de la búsqueda son inválidos")
            return SessionQuote.objects.none()

        # -- Common filters
        qs = SessionQuote.objects.visible_sessionquote(request.user)
        qs = qs.order_by('customer__name', 'name')

        if form.cleaned_data['fecha_creacion_desde']:
            qs = qs.filter(created__gte=form.cleaned_data['fecha_creacion_desde'])

        if form.cleaned_data['fecha_creacion_hasta']:
            qs = qs.filter(created__lte=form.cleaned_data['fecha_creacion_hasta'])

        # -- Specific filter for photographer/customer
        if self.request.user.is_photographer():
            qs = self._do_search_for_photographer(request, form, qs)
        else:
            qs = self._do_search_for_customer(request, form, qs)

        # ----- <Paginate> -----
        result_paginator = django_paginator.Paginator(qs, self.PAGE_RESULT_SIZE)
        try:
            qs = result_paginator.page(self.form.cleaned_data['page'])
        except django_paginator.PageNotAnInteger:  # If page is not an integer, deliver first page.
            qs = result_paginator.page(1)
        except django_paginator.EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results.
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----

        return qs

    def _do_search_for_customer(self, request, form, qs):
        """Returns QuerySet"""
        qs = qs.filter(customer=request.user.user_for_customer)
        return qs

    def _do_search_for_photographer(self, request, form, qs):
        """Returns QuerySet"""
        ARCHIVED_STATUS_ALL = forms_session_quote.SessionQuoteSearchForm.ARCHIVED_STATUS_ALL
        ARCHIVED_STATUS_ARCHIVED = forms_session_quote.SessionQuoteSearchForm.ARCHIVED_STATUS_ARCHIVED
        ARCHIVED_STATUS_ACTIVE = forms_session_quote.SessionQuoteSearchForm.ARCHIVED_STATUS_ACTIVE

        if form.cleaned_data['archived_status'] == ARCHIVED_STATUS_ALL:
            pass
        elif form.cleaned_data['archived_status'] == ARCHIVED_STATUS_ARCHIVED:
            qs = qs.filter(archived=True)
        elif form.cleaned_data['archived_status'] == ARCHIVED_STATUS_ACTIVE:
            qs = qs.exclude(archived=True)
        else:
            logger.warn("Invalid value for self.form['archived_status']: %s", form['archived_status'])

        if form.cleaned_data['customer']:
            qs = qs.filter(customer=form.cleaned_data['customer'])

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_search'] = True
        context['form'] = self.form
        # overwrites 'object_list' from `get_queryset()`
        context['object_list'] = self.search_result_qs
        context['hide_search_result'] = self.search_result_qs is None
        return context


class SessionQuoteDetailView(DetailView):
    """
    This view allows the users (both photographers & customers)
    to see the Quote and, for the customer, accept or reject.

    This is kind a 'read-only' view... The 'read-write' view is SessionQuoteAlternativeSelectView
    """
    model = SessionQuote

    def get_queryset(self):
        return SessionQuote.objects.visible_sessionquote(self.request.user)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        if 'button_update' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        elif 'button_confirm' in request.POST:
            quote.confirm(request.user)
            messages.success(self.request,
                             'El presupuesto fue confirmado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_go_to_choose_quote' in request.POST:
            return HttpResponseRedirect(reverse('quote_choose_alternative', args=[quote.id]))

        elif 'button_cancel' in request.POST:
            quote.cancel(request.user)
            messages.success(self.request,
                             'El presupuesto fue cancelado')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail',
                                                args=[quote.id]))

        # elif 'button_cancel_and_new_version' in request.POST:
        #     # TODO: implement this!
        #     messages.error(self.request, "La creacion de nuevas versiones "
        #                                  "de presupuestos todavia no esta implementada.")
        #     return HttpResponseRedirect(reverse('home'))

        elif 'button_archive_quote' in request.POST:
            quote.archived = True
            quote.save()
            messages.success(self.request, "El presupuesto fue archivado exitosamente")
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_unarchive_quote' in request.POST:
            quote.archived = False
            quote.save()
            messages.success(self.request, "El presupuesto fue recuperado exitosamente")
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_update_quote_alternatives' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        elif 'button_create_session' in request.POST:
            return HttpResponseRedirect(reverse('session_create_from_quote', args=[quote.id]))

        else:
            raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteDetailView, self).get_context_data(**kwargs)
        buttons = []

        if self.object.status == SessionQuote.STATUS_QUOTING:
            # The photographer did not finished the Quote
            if self.request.user.is_for_customer():
                # The customer shouln't see this Quote
                raise SuspiciousOperation()
            else:
                buttons.append({'name': 'button_update',
                                'submit_label': "Editar presupuesto", })
                buttons.append({'name': 'button_confirm',
                                'submit_label': "Confirmar presupuesto", 'confirm': True, })
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })

        elif self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            # Waiting for customer accept()/reject().
            # Photographer always can cancel()
            if self.request.user.is_for_customer():
                buttons.append({'name': 'button_go_to_choose_quote',
                                'submit_label': "Respdoner presupuesto (aceptar/rechazar)", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                # buttons.append({'name': 'button_cancel_and_new_version',
                #                 'submit_label': "Cancelar presupuesto y crear nueva versión",
                #                 'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presupuestos alternativos", })

        elif self.object.status == SessionQuote.STATUS_REJECTED:
            if self.request.user.is_for_customer():
                pass
            else:
                if self.object.archived:
                    buttons.append({'name': 'button_unarchive_quote',
                                    'submit_label': "Desarchivar presupuesto", })
                else:
                    buttons.append({'name': 'button_archive_quote',
                                    'submit_label': "Archivar presupuesto", })

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            if self.request.user.is_for_customer():
                # show button to change alternatives ONLY if exists more alternatives
                if self.object.get_valid_alternatives().count() > 0:
                    buttons.append({'name': 'button_go_to_choose_quote',
                                    'submit_label': "Cambiar alternativa de presupuesto", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                # buttons.append({'name': 'button_cancel_and_new_version',
                #                 'submit_label': "Cancelar presupuesto y crear nueva versión",
                #                 'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presupuestos alternativos", })
                if self.object.archived:
                    buttons.append({'name': 'button_unarchive_quote',
                                    'submit_label': "Desarchivar presupuesto", })
                else:
                    buttons.append({'name': 'button_archive_quote',
                                    'submit_label': "Archivar presupuesto", })
                if self.object.session is None:
                    buttons.append({'name': 'button_create_session',
                                    'submit_label': "Crear sesión desde presupuesto", })

        elif self.object.status == SessionQuote.STATUS_CANCELED:
            # Canceled
            if self.request.user.is_for_customer():
                pass
            else:
                if self.object.archived:
                    buttons.append({'name': 'button_unarchive_quote',
                                    'submit_label': "Desarchivar presupuesto", })
                else:
                    buttons.append({'name': 'button_archive_quote',
                                    'submit_label': "Archivar presupuesto", })

        else:
            raise Exception("Invalid 'status': {}".format(self.object.status))

        context['extra_buttons'] = buttons
        views_utils.put_session_statuses_in_context(context)

        return context


class SessionQuoteAlternativeSelectView(DetailView):
    """
    This view allows the select a quote alternative to customers.

    Only CUSTOMERS can enter this view...

    This is kind a 'read-write' view... The 'read-only' view is SessionQuoteDetailView
    """
    model = SessionQuote
    template_name = 'lumina/sessionquote_detail_choose_alternative.html'

    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_for_customer():
            raise SuspiciousOperation("The user is not a customer! User: {}".format(self.request.user))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # ATTENTION: this returns quotes the user CAN VIEW! Please, do further checks if user can modify when post()ing
        return SessionQuote.objects.visible_sessionquote(self.request.user)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        if 'button_accept' in request.POST:
            if 'accept_terms' not in request.POST:
                messages.error(self.request, 'Debe aceptar las condiciones')
                return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))
            selected_alternative = request.POST['selected_quote']

            if selected_alternative == '0':
                alternative_id = None
            else:
                alternative_id = int(selected_alternative)

            if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
                quote.accept(request.user, alternative_id)

            elif quote.status == SessionQuote.STATUS_ACCEPTED:
                assert alternative_id
                quote.update_quote_alternative(request.user, alternative_id)
            else:
                raise SuspiciousOperation()

            messages.success(self.request, 'El presupuesto fue aceptado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_reject' in request.POST:
            quote.reject(request.user)
            messages.success(self.request, 'El presupuesto fue rechazado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        else:
            raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(
            available_alternatives=self.object.get_valid_alternatives(),
            **kwargs)

        views_utils.put_session_statuses_in_context(context)

        return context


# ------------------------------------------------------------------------------------------

class SessionQuoteAlternativeCreateView(CreateView):
    model = SessionQuoteAlternative
    form_class = forms_session_quote.SessionQuoteAlternativeCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.session_quote = SessionQuote.objects.modificable_sessionquote(self.request.user).get(
            pk=self.kwargs['session_quote_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super(SessionQuoteAlternativeCreateView, self).get_initial()
        initial.update({
            'session_quote': self.session_quote
        })
        return initial

    def form_valid(self, form):
        # check unique
        qs = self.session_quote.quote_alternatives
        if qs.filter(image_quantity=form.instance.image_quantity).count() != 0:
            messages.error(self.request,
                           'Ya existe una alternativa para la cantidad de fotos ingresada')
            return self.render_to_response(self.get_context_data(form=form))

        # FIXME: check consistency between other's alternatives `image_quantity` and `cost`

        form.instance.session_quote = self.session_quote
        ret = super(SessionQuoteAlternativeCreateView, self).form_valid(form)
        messages.success(self.request, 'La alternativa fue creada correctamente')
        return ret

    def get_success_url(self):
        return reverse('quote_update', args=[self.kwargs['session_quote_id']])
