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
from lumina.mail import send_email

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
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = ImageSelection
    form_class = ImageSelectionCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_initial(self):
        initial = super(ImageSelectionCreateView, self).get_initial()
        # FIXME: filter `PreviewSize` for user's Studio
        if 'id_session' in self.request.GET:
            initial.update({
                'session': self.request.GET['id_session'],
            })
        return initial

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.customer = form.instance.session.customer
        ret = super(ImageSelectionCreateView, self).form_valid(form)

        subject = "Solicitud de seleccion de imagenes"
        link = self.request.build_absolute_uri(
            reverse('session_detail', args=[form.instance.session.id]))
        message = "Tiene una nueva solicitud para seleccionar fotografías.\n" + \
                  "Para verlo ingrese a {}".format(link)
        for customer_user in form.instance.customer.users.all():
            to_email = customer_user.email
            send_email(subject, to_email, message)

        messages.success(
            self.request, 'La solicitud de seleccion de imagenes '
                          'fue creada correctamente.')
        return ret

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.id])

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionCreateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()

        context['title'] = "Solicitud de seleccion de fotos"
        context['submit_label'] = "Enviar solicitud"
        return context
