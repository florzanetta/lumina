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


class PreviewSizeListView(ListView):
    model = models.PreviewSize

    def get_queryset(self):
        return self.request.user.get_preview_sizes()


class PreviewSizeCreateView(SuccessMessageMixin,
                            CreateView):
    model = models.PreviewSize
    form_class = forms.PreviewSizeCreateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('preview_size_list')
    success_message = 'Un nuevo tamaño de previsualización ha sido creado exitosamente'

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super().form_valid(form)
        return ret


class PreviewSizeUpdateView(SuccessMessageMixin,
                            UpdateView):
    model = models.PreviewSize
    pk_url_kwarg = 'preview_size_id'
    form_class = forms.PreviewSizeUpdateForm
    template_name = 'lumina/base_create_update_crispy_form.html'
    success_url = reverse_lazy('preview_size_list')
    success_message = 'El tamaño de previsualización ha sido actualizado exitosamente'

    def get_queryset(self):
        return self.request.user.get_preview_sizes()


class PreviewSizeArchiveView(detail.DetailView):
    model = models.PreviewSize
    pk_url_kwarg = 'preview_size_id'
    success_url = reverse_lazy('preview_size_list')

    archive = None

    def get_queryset(self):
        return self.request.user.get_preview_sizes()

    def get(self, request, *args, **kwargs):
        # FIXME: REFACTOR THIS, SHOULDN'T USE GET FOR THIS
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        assert self.archive is True or self.archive is False
        preview_size = self.get_object()
        preview_size.archived = self.archive
        preview_size.save()
        if self.archive:
            messages.success(request, "El tamaño de previsualización fue archivado exitosamente")
        else:
            messages.success(request, "El tamaño de previsualización fue recuperado exitosamente")

        return HttpResponseRedirect(self.success_url)
