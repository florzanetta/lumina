# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib import messages
from django.core.urlresolvers import reverse

from lumina.models import LuminaUser, UserPreferences
from lumina.forms import UserCreateForm, UserUpdateForm, UserPreferencesUpdateForm


__all__ = [
    'UserListView',
    'UserCreateView',
    'UserUpdateView',
]

logger = logging.getLogger(__name__)


# ===============================================================================
# User
# ===============================================================================

class UserListView(ListView):
    model = LuminaUser
    template_name = 'lumina/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        customer_id = int(self.kwargs['customer_id'])
        context['customer'] = self.request.user.all_my_customers().get(pk=customer_id)
        return context

    def get_queryset(self):
        customer_id = int(self.kwargs['customer_id'])
        return self.request.user.get_users_of_customer(customer_id)


class UserCreateView(CreateView):
    model = LuminaUser
    form_class = UserCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        return reverse('customer_user_list', kwargs={'customer_id': self.kwargs['customer_id']})

    def form_valid(self, form):
        customer = self.request.user.all_my_customers().get(pk=self.kwargs['customer_id'])
        form.instance.user_for_customer = customer
        form.instance.user_type = LuminaUser.CUSTOMER
        ret = super(UserCreateView, self).form_valid(form)

        # Set the password
        new_user = LuminaUser.objects.get(pk=form.instance.id)
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request, 'El cliente fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear usuario"
        context['submit_label'] = "Crear"
        return context


class UserUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = LuminaUser
    form_class = UserUpdateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        customer = self.get_object().user_for_customer
        return reverse('customer_user_list', kwargs={'customer_id': customer.id})

    def get_queryset(self):
        return self.request.user.get_all_users()

    def form_valid(self, form):
        ret = super(UserUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = LuminaUser.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request, 'El cliente fue actualizado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar usuario"
        context['submit_label'] = "Actualizar"
        return context


# ===============================================================================
# UserPreference
# ===============================================================================

class UserPreferenceUpdateView(UpdateView):
    model = UserPreferences
    form_class = UserPreferencesUpdateForm
    template_name = 'lumina/user_preferences_update.html'

    def get_object(self, queryset=None):
        try:
            return self.request.user.preferences
        except UserPreferences.DoesNotExist:
            UserPreferences.objects.create(user=self.request.user)
            return self.request.user.preferences

    def get_initial(self):
        initial = super().get_initial()
        initial['first_name'] = self.request.user.first_name
        initial['last_name'] = self.request.user.last_name
        initial['email'] = self.request.user.email
        initial['cellphone'] = self.request.user.cellphone
        return initial

    def get_success_url(self):
        return reverse('user_preferences_update')

    def form_valid(self, form):
        ret = super().form_valid(form)
        user = self.object.user
        if form.cleaned_data['password1']:
            user.set_password(form.cleaned_data['password1'])
            messages.success(self.request, 'Las preferencias y la contraseña fueron guardadas correctamente')
        else:
            messages.success(self.request, 'Las preferencias fueron guardados correctamente')

        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.email = form.cleaned_data['email']
        user.cellphone = form.cleaned_data['cellphone']
        user.save()
        return ret

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
