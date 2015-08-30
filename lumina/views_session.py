# -*- coding: utf-8 -*-

import base64
import json
import logging
import uuid

from django.views.generic.edit import CreateView, UpdateView, FormView, FormMixin
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core import paginator

from lumina import forms
from lumina import models


logger = logging.getLogger(__name__)


__all__ = [
    'SessionListView',
    'SessionSearchView',
    'SessionDetailView',
    'SessionCreateView',
    'SessionUpdateView',
    'SessionUploadPreviewsView',
    'session_upload_previews_upload',
]


# ===============================================================================
# Session
# ===============================================================================

class SessionListView(ListView):
    model = models.Session

    def get_context_data(self, **kwargs):
        context = super(SessionListView, self).get_context_data(**kwargs)
        context['show_add_session_button'] = True
        return context

    def get_queryset(self):
        qs = models.Session.objects.visible_sessions(self.request.user)
        qs = qs.exclude(archived=True)
        return qs.order_by('customer__name', 'name')


class SessionSearchView(ListView, FormMixin):
    model = models.Session

    PAGE_RESULT_SIZE = 2

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['photographer'] = self.request.user
        return kwargs

    def get(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=forms.SessionSearchForm)
        self.search_result_qs = None

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.form = self.get_form(form_class=forms.SessionSearchForm)
        self.search_result_qs = self._do_search(request, self.form)

        return super().get(request, *args, **kwargs)

    def _do_search(self, request, form):
        # Validate form
        if not form.is_valid():
            messages.error(request,
                           "Los parámetros de la búsqueda son inválidos")
            return models.Session.objects.none()

        # Do the search
        qs = models.Session.objects.visible_sessions(request.user)
        if form.cleaned_data['archived_status'] == forms.SessionSearchForm.ARCHIVED_STATUS_ALL:
            pass
        elif form.cleaned_data['archived_status'] == forms.SessionSearchForm.ARCHIVED_STATUS_ARCHIVED:
            qs = qs.filter(archived=True)
        elif form.cleaned_data['archived_status'] == forms.SessionSearchForm.ARCHIVED_STATUS_ACTIVE:
            qs = qs.exclude(archived=True)
        else:
            logger.warn("Invalid value for self.form['archived_status']: %s", form['archived_status'])

        if form.cleaned_data['customer']:
            qs = qs.filter(customer=form.cleaned_data['customer'])

        if form.cleaned_data['session_type']:
            qs = qs.filter(session_type=form.cleaned_data['session_type'])

        if form.cleaned_data['fecha_creacion_desde']:
            qs = qs.filter(created__gte=form.cleaned_data['fecha_creacion_desde'])

        if form.cleaned_data['fecha_creacion_hasta']:
            qs = qs.filter(created__lte=form.cleaned_data['fecha_creacion_hasta'])

        qs = qs.order_by('customer__name', 'name')

        # ----- <Paginate> -----
        result_paginator = paginator.Paginator(qs, self.PAGE_RESULT_SIZE)
        try:
            qs = result_paginator.page(self.form.cleaned_data['page'])
        except paginator.PageNotAnInteger:  # If page is not an integer, deliver first page.
            qs = result_paginator.page(1)
        except paginator.EmptyPage:  # If page is out of range (e.g. 9999), deliver last page of results.
            qs = result_paginator.page(result_paginator.num_pages)
        # ----- </Paginate> -----

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_search_form'] = True
        context['form'] = self.form
        # overwrites 'object_list' from `get_queryset()`
        context['object_list'] = self.search_result_qs
        context['hide_search_result'] = self.search_result_qs is None
        return context

    def get_queryset(self):
        return models.Session.objects.none()


class SessionDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = models.Session

    def post(self, request, *args, **kwargs):
        session = self.get_object()

        #    <input class="btn btn-primary" type="submit" name="archive_session" value="Archivar">
        #    <input class="btn btn-primary" type="submit" name="delete_session" value="Borrar">

        if 'archive_session' in request.POST:
            session.archive(self.request.user)
            messages.success(self.request, 'La sesión fue archivada correctamente')
            return HttpResponseRedirect(reverse('session_detail', args=[session.id]))

        #    if 'delete_session' in request.POST:
        #        session.delete(self.request.user)
        #        return HttpResponseRedirect(reverse('quote_update', args=[session.id]))

        raise SuspiciousOperation()

    def get_queryset(self):
        return models.Session.objects.visible_sessions(self.request.user)


class SessionCreateUpdateMixin():
    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers
        # form.fields['shared_with'].queryset = qs_customers
        form.fields['photographer'].queryset = self.request.user.studio.photographers.all()


class SessionCreateView(CreateView, SessionCreateUpdateMixin):
    model = models.Session
    form_class = forms.SessionCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_form(self, form_class):
        form = super(SessionCreateView, self).get_form(form_class)
        self._setup_form(form)
        return form

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super(SessionCreateView, self).form_valid(form)
        messages.success(self.request, 'La sesión fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear sesión"
        context['submit_label'] = "Crear"
        return context


class SessionUpdateView(UpdateView, SessionCreateUpdateMixin):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = models.Session
    form_class = forms.SessionUpdateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_form(self, form_class):
        form = super(SessionUpdateView, self).get_form(form_class)
        self._setup_form(form)
        return form

    def get_queryset(self):
        return models.Session.objects.modificable_sessions(self.request.user)

    def form_valid(self, form):
        ret = super(SessionUpdateView, self).form_valid(form)
        messages.success(self.request, 'La sesión fue actualizado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar sesión"
        context['submit_label'] = "Actualizar"
        return context


class SessionUploadPreviewsView(DetailView):
    model = models.Session
    template_name = "lumina/session_upload_previews.html"

    def get_queryset(self):
        return models.Session.objects.modificable_sessions(self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['preview_sizes'] = self.request.user.studio.preview_sizes.all()
        return context


@csrf_exempt
def session_upload_previews_upload(request, session_id):
    PREFIX = 'data:image/jpeg;base64,'
    index = 0
    img_count = 0
    session = request.user.studio.session_set.all().get(pk=session_id)
    while True:
        key = "img" + str(index)
        if key not in request.POST:
            break
        img_count += 1
        index += 1

        thumb_base64 = request.POST[key]
        filename = request.POST[key + '_filename']
        original_file_checksum = request.POST[key + '_checksum']

        # thumb_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQA(...)AP/2Q=="
        assert thumb_base64.startswith(PREFIX)
        thumb_base64 = thumb_base64[len(PREFIX):]
        thumb_contents = base64.decodestring(bytes(thumb_base64, 'ascii'))

        new_image = models.Image(session=session,
                                 studio=request.user.studio,
                                 thumbnail_content_type='image/jpg',
                                 original_file_checksum=original_file_checksum)

        new_image.set_thumbnail_original_filename(filename)
        new_image.thumbnail_size = len(thumb_contents)
        new_image.thumbnail_image.save(str(uuid.uuid4()), ContentFile(thumb_contents))
        new_image.save()

    response_data = {
        'img_count': img_count,
        'status': 'ok',
        'redirect': reverse('session_detail', args=[session.id]),
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")
