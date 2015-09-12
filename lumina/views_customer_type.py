# -*- coding: utf-8 -*-

import logging

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
        return self.request.user.all_my_customer_types()


class CustomerTypeCreateView(SuccessMessageMixin,
                             CreateView):
    model = models.CustomerType
    form_class = forms.CustomerTypeCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_type_list')
    success_message = 'Un nuevo tipo de cliente ha sido creado exitosamente'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['studio'] = self.request.user.studio
        return form_kwargs


class CustomerTypeUpdateView(SuccessMessageMixin,
                             UpdateView):
    model = models.CustomerType
    pk_url_kwarg = 'customer_type_id'
    form_class = forms.CustomerTypeUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_type_list')
    success_message = 'El tipo de cliente ha sido actualizado exitosamente'

    def get_queryset(self):
        return self.request.user.all_my_customer_types()
