# -*- coding: utf-8 -*-

import logging

from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.views import generic

from lumina import models
from lumina import forms_studio

logger = logging.getLogger(__name__)


class StudioUpdateView(generic.UpdateView):
    model = models.Studio
    form_class = forms_studio.StudioUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user.studio

    # def form_valid(self, form):
    #     ret = super().form_valid(form)
    #
    #     # Set the password
    #     if form['password1'].value():
    #         updated_user = models.LuminaUser.objects.get(pk=form.instance.id)
    #         logger.warn("Changing password of user '%s'", updated_user.username)
    #         updated_user.set_password(form['password1'].value())
    #         updated_user.save()
    #
    #     messages.success(self.request, 'El usuario fue actualizado correctamente')
    #     return ret


class StudioCreateView(generic.View):

    def get(self, request):
        return HttpResponseRedirect(reverse_lazy('home'))
