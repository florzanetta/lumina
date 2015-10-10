# -*- coding: utf-8 -*-

import logging

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse

from django.core.exceptions import SuspiciousOperation

from lumina.models import Session, ImageSelection
from lumina.forms import ImageSelectionCreateForm, ImageSelectionAutoCreateForm
from lumina.mail import send_emails_to_users

logger = logging.getLogger(__name__)


@login_required
@cache_control(private=True)
def image_selection_create_from_quote(request, pk):
    session = Session.objects.visible_sessions(request.user).get(pk=pk)
    active_quote = session.get_active_quote()
    quote_quantity, quote_cost = active_quote.get_selected_quote_values()

    assert quote_quantity > 0

    instance = ImageSelection(
        session=session,
        studio=session.studio,
        customer=session.customer,
        image_quantity=quote_quantity,
        quote=active_quote
    )

    more_photos_required_than_existing = bool(session.image_set.count() < quote_quantity)

    if request.method == 'GET':
        form = ImageSelectionAutoCreateForm(instance=instance)
        if more_photos_required_than_existing:
            messages.error(
                request, 'La sesión no contiene la cantidad de fotografías presupuestadas')

    elif request.method == 'POST':
        form = ImageSelectionAutoCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'La solicitud fue creada satisfactoriamente')
            return HttpResponseRedirect(reverse('session_detail',
                                                args=[session.id]))
        else:
            messages.error(request, 'ERROR')
    else:
        raise SuspiciousOperation("Invalid HTTP method")

    ctx = {
        'object': session,
        'form': form,
        'active_quote': active_quote,
        'quote_cost': quote_cost,
        'quote_quantity': quote_quantity,
    }

    ctx['title'] = "Solicitar selección de imágenes"
    if not more_photos_required_than_existing:
        ctx['submit_label'] = "Solicitar"

    return render_to_response(
        'lumina/imageselection_create_from_quote.html', ctx,
        context_instance=RequestContext(request))


class ImageSelectionCreateView(CreateView):
    """
    With this view, the photographer creates a request
    to the customer.
    """
    model = ImageSelection
    form_class = ImageSelectionCreateForm
    template_name = 'lumina/imageselection_create_from.html'

    def dispatch(self, request, *args, **kwargs):
        self.session = self.request.user.studio.session_set.all().get(pk=kwargs['session_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['photographer'] = self.request.user
        kwargs['session'] = self.session
        return kwargs

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.customer = form.instance.session.customer
        ret = super(ImageSelectionCreateView, self).form_valid(form)

        subject = "Solicitud de seleccion de imagenes"
        link = self.request.build_absolute_uri(
            reverse('session_detail', args=[form.instance.session.id]))
        message = "Tiene una nueva solicitud para seleccionar fotografías.\n" + \
                  "Para verlo ingrese a {}".format(link)

        send_emails_to_users(subject, form.instance.customer.users.all(), message)

        messages.success(self.request, 'La solicitud de seleccion de imagenes fue creada correctamente.')
        return ret

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.id])

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            session=self.session,
            session_doesn_have_images=bool(self.session.image_set.count() == 0),
            **kwargs)
