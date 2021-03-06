# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.urlresolvers import reverse_lazy
from django.views import generic

from lumina import models
from lumina import forms_studio
from lumina import forms_users

logger = logging.getLogger(__name__)


class StudioUpdateView(SuccessMessageMixin,
                       generic.UpdateView):
    model = models.Studio
    form_class = forms_studio.StudioUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('home')
    success_message = 'Los datos del estudio fotográfico fueron actualizados exitosamente'

    def get_object(self, queryset=None):
        return self.request.user.studio


class StudioCreateView(generic.CreateView):
    model = models.LuminaUser
    form_class = forms_users.StudioUserCreateForRegisteringNewStudioForm
    template_name = 'lumina/base_create_update_crispy_form.html'

    success_url = reverse_lazy('studio_update')

    def form_valid(self, form):
        studio_name = "Estudio de {} {}".format(form.cleaned_data['first_name'],
                                                form.cleaned_data['last_name'])
        studio = models.Studio.objects.create(name=studio_name,
                                              watermark_text=studio_name)

        form.instance.studio = studio
        form.instance.user_type = models.LuminaUser.PHOTOGRAPHER
        ret = super().form_valid(form)

        # Set the password
        new_user = models.LuminaUser.objects.get(pk=form.instance.id)
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request,
                         'La registración fue exitosa. '
                         'Ahora puedes iniciar sesión para utilizar el sistema')
        return ret
