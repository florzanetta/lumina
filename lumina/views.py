# -*- coding: utf-8 -*-

import logging
import zipfile

import os
from io import BytesIO
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import UpdateView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.contrib import messages
from django.core.files.storage import default_storage
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse

from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from lumina.pil_utils import generate_thumbnail
from lumina.models import (
    Session, Image, ImageSelection, SessionQuote, UserPreferences)
from lumina.forms import \
    UserPreferencesUpdateForm, CustomAuthenticationForm

#
# FIXME: create preference instance when creating a user
# FIXME: update password in UserPreferenceUpdateView
# FIXME: use selecte PreviewSize when generating previews
#

#
# List of generic CBV:
# - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#
# Cache:
#  - https://docs.djangoproject.com/en/1.5/topics/cache/#controlling-cache-using-other-headers
#

logger = logging.getLogger(__name__)


def login(request):
    return django_login(request, authentication_form=CustomAuthenticationForm)


def _photographer_home(request):
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
        'session_count': Session.objects.visible_sessions(request.user).count(),
        'image_selection_pending_count': ImageSelection.objects.pending_image_selections(request.user).count(),
    }
    return render_to_response(
        'lumina/index_customer.html', ctx,
        context_instance=RequestContext(request))


def _put_session_statuses_in_context(context):
    # Status de SessionQuote (reusado más abajo)
    statuses_dict = dict(SessionQuote.STATUS)
    context['status_STATUS_QUOTING'] = statuses_dict[SessionQuote.STATUS_QUOTING]
    context['status_STATUS_WAITING_CUSTOMER_RESPONSE'] = statuses_dict[
        SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE]
    context['status_STATUS_ACCEPTED'] = statuses_dict[SessionQuote.STATUS_ACCEPTED]
    context['status_STATUS_REJECTED'] = statuses_dict[SessionQuote.STATUS_REJECTED]
    context['status_STATUS_CANCELED'] = statuses_dict[SessionQuote.STATUS_CANCELED]


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
@cache_control(private=True)
def check_404(request):
    logger.info("Raising ObjectDoesNotExist()")
    raise ObjectDoesNotExist()


@login_required
@cache_control(private=True)
def check_500(request):
    logger.info("Raising Exception()")
    raise Exception()


@login_required
@cache_control(private=True)
def check_403(request):
    logger.info("Raising PermissionDenied()")
    raise PermissionDenied()


def _image_thumb(request, image, max_size=None):
    try:
        thumb = generate_thumbnail(image, max_size)
        return HttpResponse(thumb, content_type='image/jpg')
    except IOError:
        return HttpResponseRedirect('/static/unknown-icon-64x64.png')


def _image_download(request, image):
    """Sends the original uploaded file to the user"""
    full_filename = default_storage.path(image.image.path)
    filename_to_user = image.original_filename
    filesize = os.path.getsize(full_filename)
    # content_type = mimetypes.guess_type(full_filename)[0]
    content_type = image.content_type

    # TODO: send in chunks to avoid loading the file in memory
    # from django.core.servers.basehttp import FileWrapper
    #    with open(full_filename) as f:
    #        fw = FileWrapper(f)
    #        response = HttpResponse(fw, content_type=content_type)
    #        response['Content-Length'] = filesize
    #        response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
    #            filename_to_user)
    #        return response

    with open(full_filename, mode='r+b') as f:
        file_contents = f.read()
    response = HttpResponse(file_contents, content_type=content_type)
    response['Content-Length'] = filesize
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(
        filename_to_user)
    return response


def _image_download_as_zip(request, images):
    """
    Sends many images to the client.

    This methos does NOT check permissions!
    """
    # FIXME: this sholdn't be done in-memory
    # FIXME: this should be done asynchronously
    response = HttpResponse(mimetype='application/zip')

    #
    # From https://code.djangoproject.com/wiki/CookBookDynamicZip
    #

    response['Content-Disposition'] = 'filename=all.zip'
    # now add them to a zip file
    # note the zip only exist in memory as you add to it
    zip_buffer = BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)
    for an_image in images:
        zip_file.writestr(an_image.original_filename, an_image.image.read())

    zip_file.close()
    zip_buffer.flush()
    # the import detail--we return the content of the buffer
    ret_zip = zip_buffer.getvalue()
    zip_buffer.close()
    response.write(ret_zip)
    return response


@login_required
@cache_control(private=True)
def image_thumb_64x64(request, image_id):
    image = Image.objects.visible_images(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_thumb(request, image_id, max_size=None):
    image = Image.objects.visible_images(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_download(request, image_id):
    image = Image.objects.get_for_download(request.user, int(image_id))
    return _image_download(request, image)


@login_required
@cache_control(private=True)
def image_selection_download_selected_as_zip(request, image_selecion_id):
    """
    Download all the images that a customer has selected in
    a ImageSelection instance.
    """
    qs = ImageSelection.objects.all_my_accessible_imageselections(request.user)
    image_selection = qs.get(pk=image_selecion_id)
    assert image_selection.status == ImageSelection.STATUS_IMAGES_SELECTED

    images = image_selection.selected_images.all()
    return _image_download_as_zip(request, images)
