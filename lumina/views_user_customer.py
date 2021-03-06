# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic import ListView, CreateView, UpdateView

from lumina.models import LuminaUser
from lumina.forms_users import CustomerUserCreateForm, CustomerUserUpdateForm
from lumina.views_user import logger

logger = logging.getLogger(__name__)


class CustomerUserListView(ListView):
    model = LuminaUser
    template_name = 'lumina/user_list_customer.html'

    def get_context_data(self, **kwargs):
        context = super(CustomerUserListView, self).get_context_data(**kwargs)
        customer_id = int(self.kwargs['customer_id'])
        context['customer'] = self.request.user.all_my_customers().get(pk=customer_id)
        return context

    def get_queryset(self):
        customer_id = int(self.kwargs['customer_id'])
        return self.request.user.get_users_of_customer(customer_id)


class CustomerUserCreateView(CreateView):
    model = LuminaUser
    form_class = CustomerUserCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs['customer_id'] = self.kwargs['customer_id']
        return form_kwargs

    def get_success_url(self):
        return reverse('customer_user_list', kwargs={'customer_id': self.kwargs['customer_id']})

    def form_valid(self, form):
        customer = self.request.user.all_my_customers().get(pk=self.kwargs['customer_id'])
        form.instance.user_for_customer = customer
        form.instance.user_type = LuminaUser.CUSTOMER
        ret = super(CustomerUserCreateView, self).form_valid(form)

        # Set the password
        new_user = LuminaUser.objects.get(pk=form.instance.id)
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request, 'El usuario fue creado correctamente')
        return ret


class CustomerUserUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = LuminaUser
    form_class = CustomerUserUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    def get_success_url(self):
        customer = self.get_object().user_for_customer
        return reverse('customer_user_list', kwargs={'customer_id': customer.id})

    def get_queryset(self):
        return self.request.user.get_all_users_of_customers()

    def form_valid(self, form):
        ret = super(CustomerUserUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = LuminaUser.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request, 'El usuario fue actualizado correctamente')
        return ret
