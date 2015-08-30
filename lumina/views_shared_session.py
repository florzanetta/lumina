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
from lumina.mail import send_email
from lumina.views_utils import generate_thumbnail_of_image, download_image, download_image

__all__ = [
    'SharedSessionByEmailAnonymousView',
    'shared_session_by_email_image_thumb_64x64',
    'shared_session_by_email_image_download',
    'SharedSessionByEmailCreateView',
]


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
    template_name = 'lumina/base_create_update_form.html'

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.random_hash = str(uuid.uuid4())
        ret = super(SharedSessionByEmailCreateView, self).form_valid(form)

        subject = "Nuevo album compartido con Ud."
        to_email = form.instance.shared_with
        link = self.request.build_absolute_uri(
            reverse('shared_session_by_email_view', args=[form.instance.random_hash]))
        body = "Tiene un nuevo album compartido.\nPara verlo ingrese a {}".format(link)
        send_email(subject, to_email, body)

        messages.success(self.request, 'El album fue compartido correctamente')
        return ret

    def get_initial(self):
        initial = super(SharedSessionByEmailCreateView, self).get_initial()
        if 'id_session' in self.request.GET:
            initial.update({
                'session': self.request.GET['id_session'],
            })
        return initial

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.pk])

    def get_context_data(self, **kwargs):
        context = super(SharedSessionByEmailCreateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()
        context['title'] = "Compartir sesión por email"
        context['submit_label'] = "Compartir"
        return context
