# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from lumina.models import Customer
from lumina.forms import CustomerCreateForm, CustomerUpdateForm

logger = logging.getLogger(__name__)


# ===============================================================================
# Customer
# ===============================================================================

class FilterUserCusomersMixin:
    model = Customer

    def get_queryset(self):
        return self.request.user.all_my_customers()


class CustomerListView(FilterUserCusomersMixin,
                       ListView):
    template_name = 'lumina/customer_list.html'


class CustomerCreateView(FilterUserCusomersMixin,
                         SuccessMessageMixin,
                         CreateView):
    form_class = CustomerCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_list')
    success_message = 'El cliente fue creado exitosamente'

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super(CustomerCreateView, self).form_valid(form)
        return ret


class CustomerUpdateView(FilterUserCusomersMixin,
                         SuccessMessageMixin,
                         UpdateView):
    form_class = CustomerUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('customer_list')
    success_message = 'El cliente fue actualizado exitosamente'
