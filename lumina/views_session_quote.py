# -*- coding: utf-8 -*-

import logging
import decimal

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation

from lumina.models import SessionQuote, SessionQuoteAlternative
from lumina.forms import SessionQuoteCreateForm, SessionQuoteUpdateForm, \
    SessionQuoteAlternativeCreateForm, SessionQuoteUpdate2Form
from lumina.mail import send_email_for_session_quote
from lumina import views
import lumina.views_utils

__all__ = [
    'SessionQuoteCreateView',
    'SessionQuoteUpdateView',
    'SessionQuoteListView',
    'SessionQuoteDetailView',
    'SessionQuoteAlternativeSelectView',
    'SessionQuoteAlternativeCreateView',
]

logger = logging.getLogger(__name__)


# ===============================================================================
# SessionQuote
# ===============================================================================

class SessionQuoteCreateUpdateMixin():
    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers


class SessionQuoteCreateView(CreateView, SessionQuoteCreateUpdateMixin):
    model = SessionQuote
    form_class = SessionQuoteCreateForm
    template_name = 'lumina/sessionquote_create.html'

    def get_form(self, form_class):
        form = super(SessionQuoteCreateView, self).get_form(form_class)
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


class SessionQuoteUpdateView(UpdateView, SessionQuoteCreateUpdateMixin):
    """
    Allows the photographer modify a Quote.

    The SessionQuote instance is fully modificable ONLY if in state STATUS_QUOTING.
    If STATUS_WAITING_CUSTOMER_RESPONSE or STATUS_ACCEPTED, only the alternatives
    are modificables.
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = SessionQuote
    # form_class = SessionQuoteUpdateForm
    template_name = 'lumina/sessionquote_update_form.html'

    def get_form_class(self):
        if self.object.status == SessionQuote.STATUS_QUOTING:
            # modificable
            return SessionQuoteUpdateForm
        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            # ro
            return SessionQuoteUpdate2Form
        elif self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            # ro
            return SessionQuoteUpdate2Form
        else:
            raise SuspiciousOperation()

    def get_form(self, form_class):
        form = super(SessionQuoteUpdateView, self).get_form(form_class)
        if self.object.status == SessionQuote.STATUS_QUOTING:
            self._setup_form(form)
        return form

    def get_queryset(self):
        return SessionQuote.objects.modificable_sessionquote(self.request.user)

    def form_valid(self, form):
        # from Django docs:
        # > This method is called when valid form data has been POSTed.
        # > It should return an HttpResponse.

        if self.object.status == SessionQuote.STATUS_QUOTING:
            if 'default_button' in self.request.POST:  # Submit for 'Update'
                return super(SessionQuoteUpdateView, self).form_valid(form)

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

        # FIXME: add an error messages and do a redirect instead of this
        raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar presupuesto"

        if self.object.status == SessionQuote.STATUS_QUOTING:
            context['submit_label'] = "Actualizar"
            context['full_edit'] = True
        else:
            context['full_edit'] = False

        buttons = context.get('extra_buttons', [])
        buttons.append({'link_url': reverse('quote_detail', args=[self.object.id]),
                        'link_label': "Volver", })
        context['extra_buttons'] = buttons
        lumina.views_utils._put_session_statuses_in_context(context)
        return context

    def get_success_url(self):
        return reverse('quote_detail', args=[self.object.id])


class SessionQuoteListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = SessionQuote
    filter = ''

    def get_queryset(self):
        qs = SessionQuote.objects.visible_sessionquote(self.request.user)
        if self.filter == 'pending_for_customer':
            qs = qs.filter(status=SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)
        return qs.order_by('customer__name', 'id')


class SessionQuoteDetailView(DetailView):
    """
    This view allows the users (both photographers & customers)
    to see the Quote and, for the customer, accept or reject.

    This is kind a 'read-only' view... The 'read-write' view is SessionQuoteAlternativeSelectView
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
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

        elif 'button_cancel_and_new_version' in request.POST:
            # FIXME: implement this!
            messages.error(self.request, "La creacion de nuevas versiones "
                                         "de presupuestos todavia no esta implementada.")
            return HttpResponseRedirect(reverse('home'))

        elif 'button_archive_quote' in request.POST:
            # FIXME: implement this!
            messages.error(self.request, "El archivado "
                                         "de presupuestos todavia no esta implementado.")
            return HttpResponseRedirect(reverse('home'))

        elif 'button_update_quote_alternatives' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        elif 'button_create_session' in request.POST:
            new_session = quote.create_session(request.user)
            return HttpResponseRedirect(reverse('session_update', args=[new_session.id]))

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
                                'submit_label': "Editar", })
                buttons.append({'name': 'button_confirm',
                                'submit_label': "Confirmar", 'confirm': True, })
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
                buttons.append({'name': 'button_cancel_and_new_version',
                                'submit_label': "Cancelar presupuesto y crear nueva versión",
                                'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })

        elif self.object.status == SessionQuote.STATUS_REJECTED:
            if self.request.user.is_for_customer():
                pass
            else:
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            if self.request.user.is_for_customer():
                # show button to change alternatives ONLY if exists more alternatives
                if self.object.get_valid_alternatives().count() > 0:
                    buttons.append({'name': 'button_go_to_choose_quote',
                                    'submit_label': "Cambiar alternativa de presupuesto", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                buttons.append({'name': 'button_cancel_and_new_version',
                                'submit_label': "Cancelar presupuesto y crear nueva versión",
                                'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })
                if self.object.session is None:
                    buttons.append({'name': 'button_create_session',
                                    'submit_label': "Crear sesión", })

        elif self.object.status == SessionQuote.STATUS_CANCELED:
            # Canceled
            if self.request.user.is_for_customer():
                pass
            else:
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })

        else:
            raise Exception("Invalid 'status': {}".format(self.object.status))

        context['selected_quote'] = self.object.get_selected_quote()
        context['extra_buttons'] = buttons
        lumina.views_utils._put_session_statuses_in_context(context)

        return context


class SessionQuoteAlternativeSelectView(DetailView):
    """
    This view allows the select a quote alternative to customers.

    This is kind a 'read-write' view... The 'read-only' view is SessionQuoteDetailView
    """
    model = SessionQuote
    template_name = 'lumina/sessionquote_detail_choose_alternative.html'

    def get_queryset(self):
        # TODO: we should not use `visible_sessionquote()`
        return SessionQuote.objects.visible_sessionquote(self.request.user)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        if 'button_accept' in request.POST:
            if 'accept_terms' not in request.POST:
                messages.error(self.request, 'Debe aceptar las condiciones')
                return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))
            alternative = request.POST['selected_quote']

            if alternative == '0':
                params = None
            else:
                alt_quantity, alt_cost = alternative.split('_')
                params = [int(alt_quantity), decimal.Decimal(alt_cost)]

            if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
                quote.accept(request.user, params)
            elif quote.status == SessionQuote.STATUS_ACCEPTED:
                quote.update_quote_alternative(request.user, params)
            else:
                raise SuspiciousOperation()

            messages.success(self.request,
                             'El presupuesto fue aceptado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_reject' in request.POST:
            quote.reject(request.user)
            messages.success(self.request,
                             'El presupuesto fue rechazado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail',
                                                args=[quote.id]))

        else:
            raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteAlternativeSelectView, self).get_context_data(**kwargs)

        context['available_alternatives'] = self.object.get_valid_alternatives()

        if not self.request.user.is_for_customer():
            raise Exception("The user is not a customer! User: {}".format(self.request.user))

        if self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            pass

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            # Accepted or rejected -> photographer always can cancel()
            selected_quote = self.object.get_selected_quote()
            assert selected_quote >= 0
            context['selected_quote'] = selected_quote

        else:
            raise Exception("Invalid 'status': {}".format(self.object.status))

        lumina.views_utils._put_session_statuses_in_context(context)

        return context


# ------------------------------------------------------------------------------------------

class SessionQuoteAlternativeCreateView(CreateView):
    model = SessionQuoteAlternative
    form_class = SessionQuoteAlternativeCreateForm
    template_name = 'lumina/sessionquote_alternative_create_update.html'

    def get_initial(self):
        initial = super(SessionQuoteAlternativeCreateView, self).get_initial()
        session_quote_id = self.kwargs['session_quote_id']
        initial.update({'session_quote': SessionQuote.objects.get(pk=session_quote_id)})
        return initial

    def form_valid(self, form):
        session_quote_id = self.kwargs['session_quote_id']
        session_quote = SessionQuote.objects.get(pk=session_quote_id)
        # check unique
        qs = session_quote.quote_alternatives
        if qs.filter(image_quantity=form.instance.image_quantity).count() != 0:
            messages.error(self.request,
                           'Ya existe una alternativa para la cantidad de fotos ingresada')
            return self.render_to_response(self.get_context_data(form=form))

        form.instance.session_quote = session_quote
        ret = super(SessionQuoteAlternativeCreateView, self).form_valid(form)
        messages.success(self.request, 'La alternativa fue creada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteAlternativeCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear alternativa de presupuesto"
        context['submit_label'] = "Crear"

        buttons = context.get('extra_buttons', [])
        buttons.append({'link_url': reverse('quote_update',
                                            args=[self.kwargs['session_quote_id']]),
                        'link_label': "Volver", })
        context['extra_buttons'] = buttons
        return context

    def get_success_url(self):
        return reverse('quote_update', args=[self.kwargs['session_quote_id']])
