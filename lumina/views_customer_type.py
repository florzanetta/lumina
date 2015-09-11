# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
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

# class CustomerUpdateView(UpdateView):
#     # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
#     model = Customer
#     form_class = CustomerUpdateForm
#     template_name = 'lumina/base_create_update_form.html'
#     success_url = reverse_lazy('customer_list')
#
#     def get_queryset(self):
#         return self.request.user.all_my_customers()
#
#     def form_valid(self, form):
#         ret = super(CustomerUpdateView, self).form_valid(form)
#         messages.success(self.request, 'El cliente fue actualizado correctamente')
#         return ret
#
#     def get_context_data(self, **kwargs):
#         context = super(CustomerUpdateView, self).get_context_data(**kwargs)
#         context['title'] = "Actualizar cliente"
#         context['submit_label'] = "Actualizar"
#         return context
