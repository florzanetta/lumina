# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views import generic

from lumina import models
from lumina import forms_users

logger = logging.getLogger(__name__)


class StudioUserListView(generic.ListView):
    model = models.LuminaUser
    template_name = 'lumina/user_list_studio.html'

    def get_queryset(self):
        return self.request.user.get_all_photographers()


class StudioUserCreateView(generic.CreateView):
    model = models.LuminaUser
    form_class = forms_users.SetudioUserCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('studio_user_list')

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.user_type = models.LuminaUser.PHOTOGRAPHER
        ret = super().form_valid(form)

        # Set the password
        new_user = models.LuminaUser.objects.get(pk=form.instance.id)
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request, 'El usuario fue creado correctamente')
        return ret


class StudioUserUpdateView(generic.UpdateView):
    model = models.LuminaUser
    form_class = forms_users.StudioUserUpdateForm
    pk_url_kwarg = 'photographer_user_id'
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('studio_user_list')

    def get_queryset(self):
        return self.request.user.get_all_photographers()

    def form_valid(self, form):
        ret = super().form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = models.LuminaUser.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request, 'El usuario fue actualizado correctamente')
        return ret
