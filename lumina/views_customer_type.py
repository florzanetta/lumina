# -*- coding: utf-8 -*-

import logging
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from django.views.generic import detail
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from lumina import forms
from lumina import models

logger = logging.getLogger(__name__)


class CustomerTypeListView(ListView):
    model = models.CustomerType

    def get_queryset(self):
        return self.request.user.get_customer_types()


class CustomerTypeCreateView(SuccessMessageMixin,
                             CreateView):
    model = models.CustomerType
    form_class = forms.CustomerTypeCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_type_list')
    success_message = 'Un nuevo tipo de cliente ha sido creado exitosamente'

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super().form_valid(form)
        return ret


class CustomerTypeUpdateView(SuccessMessageMixin,
                             UpdateView):
    model = models.CustomerType
    pk_url_kwarg = 'customer_type_id'
    form_class = forms.CustomerTypeUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_type_list')
    success_message = 'El tipo de cliente ha sido actualizado exitosamente'

    def get_queryset(self):
        return self.request.user.get_customer_types()


class CustomerTypeArchiveView(detail.DetailView):
    model = models.CustomerType
    pk_url_kwarg = 'customer_type_id'
    success_url = reverse_lazy('customer_type_list')

    archive = None

    def get_queryset(self):
        return self.request.user.get_customer_types()

    def get(self, request, *args, **kwargs):
        # FIXME: REFACTOR THIS, SHOULDN'T USE GET FOR THIS
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        assert self.archive is True or self.archive is False
        customer_type = self.get_object()
        customer_type.archived = self.archive
        customer_type.save()
        if self.archive:
            messages.success(request, "El tipo de usuario fue archivado exitosamente")
        else:
            messages.success(request, "El tipo de usuario fue recuperado exitosamente")

        return HttpResponseRedirect(self.success_url)
