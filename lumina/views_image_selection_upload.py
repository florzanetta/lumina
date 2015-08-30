# -*- coding: utf-8 -*-

import hashlib
import json
import logging
import uuid

from django.core.files.base import ContentFile
from django.shortcuts import redirect
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, Http404
from django.http.response import HttpResponseRedirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from lumina.models import Image, ImageSelection
from lumina.views_image_selection import logger


logger = logging.getLogger(__name__)


class UploadPendingManualView(DetailView):
    model = ImageSelection
    template_name = 'lumina/imageselection_upload_pending_manual.html'

    def get(self, *args, **kwargs):
        try:
            return super(UploadPendingManualView, self).get(*args, **kwargs)
        except Http404:
            return redirect(reverse('imageselection_upload_pending_all_images_aready_uploaded',
                                    args=[kwargs[self.pk_url_kwarg]]))

    def get_queryset(self):
        return ImageSelection.objects.full_quality_pending_uploads(
            self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UploadPendingManualView, self).get_context_data(**kwargs)
        context['selected_images_without_full_quality'] = \
            self.object.get_selected_images_without_full_quality()
        return context

    def post(self, request, pk, *args, **kwargs):
        image_selection = self.get_queryset().get(pk=pk)
        for just_uploaded_key, a_file in list(request.FILES.items()):
            assert just_uploaded_key.startswith('file_for_')
            splitted_key = just_uploaded_key.split('_')
            assert len(splitted_key) == 3
            image_pk = splitted_key[2]
            image = Image.objects.get(pk=image_pk)
            assert image.session == image_selection.session
            assert image.image in (None, ''), "No es none: {}".format(image.image)
            image.image = a_file
            image.size = a_file.size
            image.set_original_filename(a_file.name)
            image.set_content_type(a_file.content_type)
            image.save()

        messages.success(self.request, 'Se subieron correctamente {} imágenes'.format(
            len(request.FILES)))
        # Don't use get_queryset(), won't work without pending uploads
        cnt = ImageSelection.objects.get(pk=pk).get_selected_images_without_full_quality().count()
        if cnt == 0:
            messages.success(self.request,
                             'Se finalizó la carga. Todas las imagenes seleccionadas por el cliente '
                             'poseen la versión en calidad total.')
            # TODO: send email to customer telling the files are ready to be downloaded
            return HttpResponseRedirect(reverse('imageselection_redirect',
                                                args=[pk]))
        else:
            return HttpResponseRedirect(reverse('imageselection_upload_pending_manual',
                                                args=[pk]))


class UploadPendingAutomaticView(DetailView):
    """
    Upload originial images, automating the selection of the images
    using the checksum of the original images (uploaded when the previews
    where uploaded).
    """
    model = ImageSelection
    template_name = 'lumina/imageselection_upload_pending_automatic.html'

    def get_queryset(self):
        return ImageSelection.objects.full_quality_pending_uploads(
            self.request.user)

    def get(self, *args, **kwargs):
        try:
            return super(UploadPendingAutomaticView, self).get(*args, **kwargs)
        except Http404:
            return redirect(reverse('imageselection_upload_pending_all_images_aready_uploaded',
                                    args=[kwargs[self.pk_url_kwarg]]))

    def get_context_data(self, **kwargs):
        context = super(UploadPendingAutomaticView, self).get_context_data(**kwargs)
        context['selected_images_without_full_quality'] = \
            self.object.get_selected_images_without_full_quality()
        return context

    def post(self, request, *args, **kwargs):
        """
        This post receives the upload, one by one, of the files in full-quality,
        using Ajax and checking the checksum in client-side
        """
        client_calculated_checksum = request.GET['checksum']
        client_reported_image_id = request.GET['imageId']
        binary_data = request.body
        logger.debug("Receiving full-quality image - checksum: %s - imageId: %s - length: %s",
                     client_calculated_checksum,
                     client_reported_image_id,
                     len(binary_data))

        md5sum_hasher = hashlib.md5()
        md5sum_hasher.update(binary_data)
        claculated_checksum = md5sum_hasher.hexdigest()

        if client_calculated_checksum != claculated_checksum:
            logger.warn("client_calculated_checksum != claculated_checksum - client: %s - server: %s",
                        client_calculated_checksum,
                        claculated_checksum)
            response_data = {
                'status': 'error',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        image = self.get_object().selected_images.get(pk=int(client_reported_image_id))
        if claculated_checksum != image.original_file_checksum:
            logger.warn("claculated_checksum != image.original_file_checksum - calculated: %s - original: %s",
                        claculated_checksum,
                        image.original_file_checksum)
            response_data = {
                'status': 'error',
            }
            return HttpResponse(json.dumps(response_data), content_type="application/json")

        image.image.save(str(uuid.uuid4()), ContentFile(binary_data))
        image.save()

        response_data = {
            'status': 'ok',
            'img_count': 1,
            'claculated_checksum': claculated_checksum
        }
        return HttpResponse(json.dumps(response_data), content_type="application/json")


class UploadPendingAllImagesAlreadyUploadedView(DetailView):
    """Show error message when all the images where uploaded"""
    model = ImageSelection
    template_name = "lumina/imageselection_upload_all_images_aready_uploaded.html"

    def get_queryset(self):
        return ImageSelection.objects.all_my_accessible_imageselections(self.request.user)
