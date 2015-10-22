# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse

from lumina.models import Session, Image, ImageSelection, SessionQuote
from lumina.forms import CustomAuthenticationForm
from lumina.views_utils import generate_thumbnail_of_image, download_image, is_mobile, serve_image_or_thumb


#
# FIXME: update password in UserPreferenceUpdateView
# FIXME: use selecte PreviewSize when generating previews
#

logger = logging.getLogger(__name__)


def login(request):
    return django_login(request, authentication_form=CustomAuthenticationForm)


def _photographer_home(request):

    if is_mobile(request):
        return HttpResponseRedirect(reverse('session_list'))

    image_selection_with_pending_uploads = \
        ImageSelection.objects.full_quality_pending_uploads(
            request.user)
    image_selection_with_pending_uploads_count = image_selection_with_pending_uploads.count()

    ctx = {
        'session_count': Session.objects.visible_sessions(request.user).count(),
        'image_count': Image.objects.visible_images(request.user).count(),
        'shared_session_via_email_count': request.user.all_my_shared_sessions_by_email().count(),
        'image_selection_with_pending_uploads': image_selection_with_pending_uploads,
        'image_selection_with_pending_uploads_count': image_selection_with_pending_uploads_count,
    }
    return render_to_response(
        'lumina/index_photographer.html', ctx,
        context_instance=RequestContext(request))


def _customer_home(request):
    ctx = {
        'quotes_pending_count': SessionQuote.objects.get_waiting_for_customer_response(request.user).count(),
        'image_selection_pending_count': ImageSelection.objects.pending_image_selections(request.user).count(),
    }
    return render_to_response(
        'lumina/index_customer.html', ctx,
        context_instance=RequestContext(request))


def home(request):
    if not request.user.is_authenticated():
        # ----- Anonymous
        ctx = {}
        return render_to_response(
            'lumina/index_anonymous.html', ctx,
            context_instance=RequestContext(request))

    request.user._check()

    if request.user.is_photographer():
        # ----- Photographer
        return _photographer_home(request)
    else:
        # ----- Customer
        return _customer_home(request)


@login_required
@cache_control(private=True, max_age=settings.LUMINA_THUMBNAIL_CACHE)
def image_thumb_64x64(request, image_id):
    image = Image.objects.visible_images(request.user).get(pk=image_id)
    return generate_thumbnail_of_image(request, image, 64)


@login_required
@cache_control(private=True, max_age=settings.LUMINA_THUMBNAIL_CACHE)
def image_thumb_200x200(request, image_id):
    image = Image.objects.visible_images(request.user).get(pk=image_id)
    return generate_thumbnail_of_image(request, image, 200)


@login_required
@cache_control(private=True, max_age=settings.LUMINA_THUMBNAIL_CACHE)
def image_thumb(request, image_id):
    image = Image.objects.visible_images(request.user).get(pk=image_id)
    return generate_thumbnail_of_image(request, image, 64)


@login_required
@cache_control(private=True)
def image_download(request, image_id):
    image = Image.objects.get_for_download(request.user, int(image_id))
    return download_image(request, image)


@login_required
@cache_control(private=True)
def get_image_or_thumb(request, image_id):
    image = Image.objects.get_for_download(request.user, int(image_id))
    return serve_image_or_thumb(request, image)
