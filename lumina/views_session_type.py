# -*- coding: utf-8 -*-

import logging
from django.contrib import messages
from django.http.response import HttpResponseRedirect

from django.views.generic import detail
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.core.urlresolvers import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin

from lumina import forms
from lumina import models

logger = logging.getLogger(__name__)


class SessionTypeListView(ListView):
    model = models.SessionType

    def get_queryset(self):
        return self.request.user.get_session_types()


class SessionTypeCreateView(SuccessMessageMixin,
                            CreateView):
    model = models.SessionType
    form_class = forms.SessionTypeCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('session_type_list')
    success_message = 'Un nuevo tipo de cliente ha sido creado exitosamente'

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        # Required so ModelForm can validate uniqueness
        form_kwargs['instance'] = models.SessionType(studio=self.request.user.studio)
        return form_kwargs

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super().form_valid(form)
        return ret


class SessionTypeUpdateView(SuccessMessageMixin,
                            UpdateView):
    model = models.SessionType
    pk_url_kwarg = 'session_type_id'
    form_class = forms.SessionTypeUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('session_type_list')
    success_message = 'El tipo de cliente ha sido actualizado exitosamente'

    def get_queryset(self):
        return self.request.user.get_session_types()


class SessionTypeArchiveView(detail.DetailView):
    model = models.SessionType
    pk_url_kwarg = 'session_type_id'
    success_url = reverse_lazy('session_type_list')

    archive = None

    def get_queryset(self):
        return self.request.user.get_session_types()

    def get(self, request, *args, **kwargs):
        # FIXME: REFACTOR THIS, SHOULDN'T USE GET FOR THIS
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        assert self.archive is True or self.archive is False
        session_type = self.get_object()
        session_type.archived = self.archive
        session_type.save()
        if self.archive:
            messages.success(request, "El tipo de sesión fotográfica fue archivada exitosamente")
        else:
            messages.success(request, "El tipo de sesión fotográfica fue recuperada exitosamente")

        return HttpResponseRedirect(self.success_url)
