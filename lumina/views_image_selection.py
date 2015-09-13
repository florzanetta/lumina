# -*- coding: utf-8 -*-

import logging

from django.conf import settings
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse

from django.core.exceptions import SuspiciousOperation

from lumina.models import ImageSelection
from lumina.mail import send_emails_to_users
from lumina import views_utils
from lumina.views_utils import download_images_as_zip

logger = logging.getLogger(__name__)


# ===============================================================================
# ImageSelection
# ===============================================================================

@login_required
@cache_control(private=True)
def imageselection_redirect(request, pk):
    """
    Redirects to the proper page, depending on:
    - user's role (photograper / customre)
    - ImageSelection state
    """
    imageselection_id = int(pk)
    imageselection = ImageSelection.objects.all_my_accessible_imageselections(
        request.user).get(id=imageselection_id)
    assert isinstance(imageselection, ImageSelection)

    if request.user.is_photographer():
        # The photograper is always sent to the 'details' page
        return HttpResponseRedirect(reverse('imageselection_detail', args=[imageselection_id]))
    elif request.user.is_for_customer():
        # The customer is redirected depending on the state of ImageSelection
        if imageselection.status == ImageSelection.STATUS_IMAGES_SELECTED:
            # The customer did the selection -> redirect to 'details' page
            return HttpResponseRedirect(reverse('imageselection_detail', args=[imageselection_id]))
        else:
            return HttpResponseRedirect(reverse('imageselection_select_images',
                                                args=[imageselection_id]))


class ImageSelectionListView(ListView):
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.all_my_imageselections_as_customer(self.request.user)


class ImageSelectionWithPendingUploadsListView(ListView):
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.full_quality_pending_uploads(
            self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionWithPendingUploadsListView, self).get_context_data(**kwargs)
        context['for_pending_uploads'] = True
        return context


class ImageSelectionForCustomerView(DetailView):
    """
    With this view, the customer selects the images he/she wants.
    """
    # Here we use DetailView instead of UpdateView because we
    # can't use a form to set the MtoM, so it's easier to use
    # the model instance + request values
    model = ImageSelection
    template_name = 'lumina/imageselection_update_for_customer_form.html'

    def get_queryset(self):
        return ImageSelection.objects.all_my_imageselections_as_customer(self.request.user,
                                                                         just_pending=True)

    def post(self, request, *args, **kwargs):
        image_selection = self.get_object()
        assert isinstance(image_selection, ImageSelection)
        selected_images_ids = request.POST.getlist('selected_images')
        if len(selected_images_ids) != image_selection.image_quantity:
            messages.error(self.request,
                           'Debe seleccionar {} imagen/es'.format(image_selection.image_quantity))
            return HttpResponseRedirect(reverse('imageselection_select_images',
                                                args=[image_selection.id]))

        # use `str` to compare, to avoid conversion to `int`
        images = image_selection.session.image_set.all()
        allowed_images_id = [str(img.id) for img in images]
        invalid_ids = [img_id for img_id in selected_images_ids if img_id not in allowed_images_id]

        if invalid_ids:
            # This was an attempt to submit ids for images on other's albums!
            raise SuspiciousOperation("Invalid ids: {}".format(','.join(invalid_ids)))

        images_by_id = dict([(img.id, img) for img in images])
        for img_id in selected_images_ids:
            img_id = int(img_id)
            image_selection.selected_images.add(images_by_id[img_id])
        image_selection.status = ImageSelection.STATUS_IMAGES_SELECTED
        image_selection.save()

        # --- <mail> ---
        subject = "El cliente ha realizado su selección"
        link = self.request.build_absolute_uri(
            reverse('imageselection_detail', args=[image_selection.id]))
        body = "El cliente ha seleccionado las imagenes de la sesion.\n" + \
               "Para verlo ingrese a {}".format(link)
        send_emails_to_users(subject, image_selection.studio.photographers.all(), body)
        # --- </mail> ---

        messages.success(self.request, 'La seleccion fue guardada correctamente')
        return HttpResponseRedirect(reverse('imageselection_detail',
                                            args=[image_selection.id]))


class ImageSelectionDetailView(DetailView):
    """
    This view shows in read-only an ImageSelectoin instance.

    This should be used for album's owner, and the customer (only
    after he/she has selected the images).
    """
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.all_my_accessible_imageselections(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ImageSelectionDetailView, self).get_context_data(**kwargs)
        image_selection = self.object
        assert isinstance(image_selection, ImageSelection)

        # Compare `id` because of the use of UserProxyManager
        if self.request.user.is_photographer():
            # Show all to the photographer
            if image_selection.session.studio != self.request.user.studio:
                raise SuspiciousOperation()
            ctx['images_to_show'] = image_selection.session.image_set.all()
            selected_images = image_selection.selected_images.all()

            # Check if all the selected images are avaiable in full-quality
            all_selected_are_available_in_full_quality = True
            for image in selected_images:
                if not image.image:
                    all_selected_are_available_in_full_quality = False
                    break

            if all_selected_are_available_in_full_quality:
                if image_selection.status == ImageSelection.STATUS_IMAGES_SELECTED:
                    ctx['show_download_selected_as_zip_button'] = True
            else:
                messages.warning(self.request,
                                 'Algunas imagenes todavía no estan disponibles para ser bajadas en calidad total')

        elif self.request.user.is_for_customer():
            # Show only selected images to customer
            if image_selection.session.customer != self.request.user.user_for_customer:
                raise SuspiciousOperation
            ctx['images_to_show'] = image_selection.selected_images.all()

            # Check if all the selected images are avaiable in full-quality
            all_selected_are_available_in_full_quality = True
            for image in ctx['images_to_show']:
                if not image.image:
                    all_selected_are_available_in_full_quality = False
                    break

            if all_selected_are_available_in_full_quality:
                if image_selection.status == ImageSelection.STATUS_IMAGES_SELECTED:
                    ctx['show_download_selected_as_zip_button'] = True
            else:
                messages.warning(self.request,
                                 'Algunas imagenes todavía no estan disponibles para ser bajadas en calidad total')

        else:
            raise SuspiciousOperation()

        return ctx


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
    return download_images_as_zip(request, images)


@login_required
@cache_control(private=True, max_age=settings.LUMINA_THUMBNAIL_CACHE)
def image_selection_thumbnail(request, image_selection_id, image_id):
    qs = ImageSelection.objects.all_my_accessible_imageselections(request.user)
    image_selection = qs.get(pk=image_selection_id)
    image = image_selection.session.image_set.get(pk=image_id)

    return views_utils.generate_thumbnail_of_image(request,
                                                   image,
                                                   image_selection.preview_size.max_size,
                                                   add_watermark=True)
