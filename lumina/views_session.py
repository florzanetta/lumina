# -*- coding: utf-8 -*-

import base64
import json
import logging
import uuid

from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from lumina.models import Session, Image
from lumina.forms import SessionCreateForm, SessionUpdateForm

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
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionListView, self).get_context_data(**kwargs)
        return context

    def get_queryset(self):
        qs = Session.objects.visible_sessions(self.request.user)
        qs = qs.exclude(archived=True)
        return qs.order_by('customer__name', 'name')


class SessionSearchView(ListView):
    model = Session

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['list_archived'] = True
        return context

    def get_queryset(self):
        qs = Session.objects.visible_sessions(self.request.user)
        qs = qs.filter(archived=True)
        return qs.order_by('customer__name', 'name')


class SessionDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = Session

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
        return Session.objects.visible_sessions(self.request.user)


class SessionCreateUpdateMixin():
    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers
        # form.fields['shared_with'].queryset = qs_customers
        form.fields['photographer'].queryset = self.request.user.studio.photographers.all()


class SessionCreateView(CreateView, SessionCreateUpdateMixin):
    model = Session
    form_class = SessionCreateForm
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
    model = Session
    form_class = SessionUpdateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_form(self, form_class):
        form = super(SessionUpdateView, self).get_form(form_class)
        self._setup_form(form)
        return form

    def get_queryset(self):
        return Session.objects.modificable_sessions(self.request.user)

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
    model = Session
    template_name = "lumina/session_upload_previews.html"

    def get_queryset(self):
        return Session.objects.modificable_sessions(self.request.user)

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

        new_image = Image(session=session, studio=request.user.studio,
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
