# -*- coding: utf-8 -*-

import logging

from django.views.generic.edit import UpdateView
from django.contrib import messages
from django.core.urlresolvers import reverse

from lumina.models import UserPreferences
from lumina.forms import UserPreferencesUpdateForm


logger = logging.getLogger(__name__)


class UserPreferenceUpdateView(UpdateView):
    model = UserPreferences
    form_class = UserPreferencesUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    def get_object(self, queryset=None):
        return self.request.user.get_or_create_user_preferences()

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
