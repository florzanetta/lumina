# -*- coding: utf-8 -*-

import uuid

from django.conf import settings
from django.views.generic.edit import CreateView
from django.views.generic.detail import DetailView
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse

from lumina.models import SharedSessionByEmail
from lumina.forms import SharedSessionByEmailCreateForm
from lumina.mail import send_emails
from lumina.views_utils import generate_thumbnail_of_image, download_image

from lumina import models
from lumina import forms


# ===============================================================================
# SharedSessionByEmail (ex: SharedAlbum)
# ===============================================================================

class SharedSessionByEmailAnonymousView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = SharedSessionByEmail
    slug_url_kwarg = 'random_hash'
    slug_field = 'random_hash'
    template_name = 'lumina/sharedalbum_anonymous_view.html'


@cache_control(private=True, max_age=settings.LUMINA_THUMBNAIL_CACHE)
def shared_session_by_email_image_thumb_64x64(request, random_hash, image_id):
    shared_album = SharedSessionByEmail.objects.get(random_hash=random_hash)
    return generate_thumbnail_of_image(request, shared_album.get_image_from_session(image_id), 64)


@cache_control(private=True)
def shared_session_by_email_image_download(request, random_hash, image_id):
    shared_album = SharedSessionByEmail.objects.get(random_hash=random_hash)
    image = shared_album.get_image_from_session(image_id)
    return download_image(request, image)


class SharedSessionByEmailCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = SharedSessionByEmail
    form_class = SharedSessionByEmailCreateForm
    template_name = 'lumina/session_share_by_email.html'
    pk_url_kwarg = 'session_id'

    def _get_queryset(self):
        return models.Session.objects.visible_sessions(self.request.user)

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.random_hash = str(uuid.uuid4())
        ret = super().form_valid(form)

        subject = "Nuevo album compartido con Ud."
        to_email = form.instance.shared_with
        link = self.request.build_absolute_uri(
            reverse('shared_session_by_email_view', args=[form.instance.random_hash]))
        body = "Tiene un nuevo album compartido.\nPara verlo ingrese a {}".format(link)
        send_emails(subject, [to_email], body)

        messages.success(self.request, 'El album fue compartido correctamente')
        return ret

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        session_id = self.kwargs[self.pk_url_kwarg]
        form_kwargs['session'] = self._get_queryset().get(pk=session_id)
        return form_kwargs

    def get_context_data(self, **kwargs):
        session_id = self.kwargs[self.pk_url_kwarg]
        return super().get_context_data(
            session=self._get_queryset().get(pk=session_id),
            **kwargs
        )

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.pk])
