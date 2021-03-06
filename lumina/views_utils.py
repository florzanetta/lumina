# -*- coding: utf-8 -*-

import logging
import os
import zipfile

from io import BytesIO
from django.core.files.storage import default_storage
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

import django_mobile

from lumina import models
from lumina.models import SessionQuote
from lumina.pil_utils import generate_thumbnail


logger = logging.getLogger(__name__)


def is_mobile(request):
    return django_mobile.get_flavour(request) == "mobile"


def put_session_statuses_in_context(context):
    # Status de SessionQuote (reusado más abajo)
    statuses_dict = dict(SessionQuote.STATUS)
    context['status_STATUS_QUOTING'] = statuses_dict[SessionQuote.STATUS_QUOTING]
    context['status_STATUS_WAITING_CUSTOMER_RESPONSE'] = statuses_dict[
        SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE]
    context['status_STATUS_ACCEPTED'] = statuses_dict[SessionQuote.STATUS_ACCEPTED]
    context['status_STATUS_REJECTED'] = statuses_dict[SessionQuote.STATUS_REJECTED]
    context['status_STATUS_CANCELED'] = statuses_dict[SessionQuote.STATUS_CANCELED]


def generate_thumbnail_of_image(request, image, *args, **kwargs):
    """Returns an HttoResponse with a thumbnail of the image.

    The '*args' and '**kwargs' are passed to `generate_thumbnail()`
    """
    try:
        thumb = generate_thumbnail(image, *args, **kwargs)
        return HttpResponse(thumb, content_type='image/jpg')
    except IOError:
        logger.exception("Couldn't generate thumbnail for image %s", image.id)
        return HttpResponseRedirect('/static/lumina/img/unknown-icon-64x64.png')


def serve_image_or_thumb(request, image):
    assert isinstance(image, models.Image)

    file_obj = image.get_image_or_thumbnail_file()
    full_filename = default_storage.path(file_obj.path)
    filesize = os.path.getsize(full_filename)
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
    return response


def download_image(request, image):
    """Sends the original uploaded file to the user"""
    full_filename = default_storage.path(image.image.path)
    filename_to_user = image.original_filename or image.thumbnail_original_filename
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
    response['Content-Disposition'] = 'attachment; filename="{0}"'.format(filename_to_user)
    return response


def download_images_as_zip(request, images):
    """
    Sends many images to the client.

    This methos does NOT check permissions!
    """
    # FIXME: this sholdn't be done in-memory
    # FIXME: this should be done asynchronously
    response = HttpResponse(content_type='application/zip')

    #
    # From https://code.djangoproject.com/wiki/CookBookDynamicZip
    #

    response['Content-Disposition'] = 'filename=all.zip'
    # now add them to a zip file
    # note the zip only exist in memory as you add to it
    zip_buffer = BytesIO()
    zip_file = zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED)
    for an_image in images:
        zip_file.writestr(an_image.original_filename or an_image.thumbnail_original_filename, an_image.image.read())

    zip_file.close()
    zip_buffer.flush()
    # the import detail--we return the content of the buffer
    ret_zip = zip_buffer.getvalue()
    zip_buffer.close()
    response.write(ret_zip)
    return response


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
