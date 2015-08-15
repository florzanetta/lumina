# -*- coding: utf-8 -*-

import logging

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse
from django.core.exceptions import SuspiciousOperation

from lumina.models import Session, Image, ImageSelection
from lumina.forms import ImageSelectionCreateForm, ImageSelectionAutoCreateForm
from lumina.mail import send_email


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
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.all_my_imageselections_as_customer(self.request.user)


class ImageSelectionWithPendingUploadsListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.full_quality_pending_uploads(
            self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionWithPendingUploadsListView, self).get_context_data(**kwargs)
        context['for_pending_uploads'] = True
        return context


class ImageSelectionUploadPendingView(DetailView):
    model = ImageSelection
    template_name = 'lumina/imageselection_upload_pending.html'

    def get_queryset(self):
        return ImageSelection.objects.full_quality_pending_uploads(
            self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionUploadPendingView, self).get_context_data(**kwargs)
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
            return HttpResponseRedirect(reverse('imageselection_upload_pending',
                                                args=[pk]))


class ImageSelectionCreateView(CreateView):
    """
    With this view, the photographer creates a request
    to the customer.
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = ImageSelection
    form_class = ImageSelectionCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_initial(self):
        initial = super(ImageSelectionCreateView, self).get_initial()
        # FIXME: filter `PreviewSize` for user's Studio
        if 'id_session' in self.request.GET:
            initial.update({
                'session': self.request.GET['id_session'],
            })
        return initial

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        form.instance.customer = form.instance.session.customer
        ret = super(ImageSelectionCreateView, self).form_valid(form)

        subject = "Solicitud de seleccion de imagenes"
        link = self.request.build_absolute_uri(
            reverse('session_detail', args=[form.instance.session.id]))
        message = "Tiene una nueva solicitud para seleccionar fotografías.\n" + \
                  "Para verlo ingrese a {}".format(link)
        for customer_user in form.instance.customer.users.all():
            to_email = customer_user.email
            send_email(subject, to_email, message)

        messages.success(
            self.request, 'La solicitud de seleccion de imagenes '
                          'fue creada correctamente.')
        return ret

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.id])

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionCreateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()

        context['title'] = "Solicitud de seleccion de fotos"
        context['submit_label'] = "Enviar solicitud"
        return context


@login_required
@cache_control(private=True)
def image_selection_create_from_quote(request, pk):
    session = Session.objects.visible_sessions(request.user).get(pk=pk)
    active_quote = session.get_active_quote()
    quote_quantity, quote_cost = active_quote.get_selected_quote_values()

    assert quote_quantity > 0

    instance = ImageSelection(
        session=session,
        studio=session.studio,
        customer=session.customer,
        image_quantity=quote_quantity,
        quote=active_quote
    )

    more_photos_required_than_existing = bool(session.image_set.count() < quote_quantity)

    if request.method == 'GET':
        form = ImageSelectionAutoCreateForm(instance=instance)
        if more_photos_required_than_existing:
            messages.error(
                request, 'La sesión no contiene la cantidad de fotografías presupuestadas')

    elif request.method == 'POST':
        form = ImageSelectionAutoCreateForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, 'La solicitud fue creada satisfactoriamente')
            return HttpResponseRedirect(reverse('session_detail',
                                                args=[session.id]))
        else:
            messages.error(request, 'ERROR')
    else:
        raise SuspiciousOperation("Invalid HTTP method")

    ctx = {
        'object': session,
        'form': form,
        'active_quote': active_quote,
        'quote_cost': quote_cost,
        'quote_quantity': quote_quantity,
    }

    ctx['title'] = "Solicitar selección de imágenes"
    if not more_photos_required_than_existing:
        ctx['submit_label'] = "Solicitar"

    return render_to_response(
        'lumina/imageselection_create_from_quote.html', ctx,
        context_instance=RequestContext(request))


# class ImageSelectionAutoCreateView(DetailView):
#    """
#    With this view, the photographer creates a request
#    to the customer when the session has a quote associated.
#    """
#    model = Session
#    template_name = 'lumina/imageselection_create_from_quote.html'
#
#    def get_queryset(self):
#        # FIXME: `visible_sessions()` shouldn't be used here!
#        return Session.objects.visible_sessions(self.request.user)
#
#    def get_context_data(self, **kwargs):
#        context = super(ImageSelectionAutoCreateView, self).get_context_data(**kwargs)
#        context['form'] = ImageSelectionAutoCreateForm()
#        return context


class ImageSelectionForCustomerView(DetailView):
    """
    With this view, the customer selects the images he/she wants.
    """
    # Here we use DetailView instead of UpdateView because we
    # can't use a form to set the MtoM, so it's easier to use
    # the model instance + request values
    #
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
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

        subject = "El cliente ha realizado su selección"
        for photographer in image_selection.studio.photographers.all():
            to_email = photographer.email
            link = self.request.build_absolute_uri(
                reverse('imageselection_detail', args=[image_selection.id]))
            body = "El cliente ha seleccionado las imagenes de la sesion.\n" + \
                   "Para verlo ingrese a {}".format(link)
            send_email(subject, to_email, body)

        messages.success(self.request, 'La seleccion fue guardada correctamente')
        return HttpResponseRedirect(reverse('imageselection_detail',
                                            args=[image_selection.id]))


class ImageSelectionDetailView(DetailView):
    """
    This view shows in read-only an ImageSelectoin instance.

    This should be used for album's owner, and the customer (only
    after he/she has selected the images).
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = ImageSelection

    def get_queryset(self):
        return ImageSelection.objects.all_my_accessible_imageselections(self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super(ImageSelectionDetailView, self).get_context_data(**kwargs)
        image_selection = ctx['object']
        assert isinstance(image_selection, ImageSelection)

        # Compare `id` because of the use of UserProxyManager
        if self.request.user.is_photographer():
            # Show all to the photographer
            if image_selection.session.studio != self.request.user.studio:
                raise SuspiciousOperation()
            ctx['images_to_show'] = image_selection.session.image_set.all()
            ctx['selected_images'] = image_selection.selected_images.all()

            # Check if all the selected images are avaiable in full-quality
            all_selected_are_available_in_full_quality = True
            for image in ctx['selected_images']:
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
