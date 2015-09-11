# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy

from lumina import models
from lumina.forms import CustomerCreateForm, CustomerUpdateForm

logger = logging.getLogger(__name__)


class CustomerTypeListView(ListView):
    model = models.CustomerType

    def get_queryset(self):
        return self.request.user.all_my_customer_types()


# class CustomerCreateView(CreateView):
#     model = Customer
#     form_class = CustomerCreateForm
#     template_name = 'lumina/base_create_update_form.html'
#     success_url = reverse_lazy('customer_list')
#
#     def form_valid(self, form):
#         form.instance.studio = self.request.user.studio
#         ret = super(CustomerCreateView, self).form_valid(form)
#         messages.success(self.request, 'El cliente fue creado correctamente')
#         return ret
#
#     def get_context_data(self, **kwargs):
#         context = super(CustomerCreateView, self).get_context_data(**kwargs)
#         context['title'] = "Agregar cliente"
#         context['submit_label'] = "Agregar"
#         return context
#
#
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
