# -*- coding: utf-8 -*-

import base64
import json
import logging
import os
import uuid
import decimal
import zipfile

from io import StringIO

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as django_login
from django.contrib import messages
from django.core.files.storage import default_storage
from django.views.decorators.cache import cache_control
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import SuspiciousOperation, ObjectDoesNotExist, \
    PermissionDenied
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile

from lumina.pil_utils import generate_thumbnail
from lumina.models import Session, Image, LuminaUser, Customer, \
    SharedSessionByEmail, ImageSelection, SessionQuote, SessionQuoteAlternative, \
    UserPreferences
from lumina.forms import SessionCreateForm, SessionUpdateForm, \
    CustomerCreateForm, CustomerUpdateForm, UserCreateForm, UserUpdateForm, \
    SharedSessionByEmailCreateForm, ImageCreateForm, ImageUpdateForm, \
    ImageSelectionCreateForm, SessionQuoteCreateForm, SessionQuoteUpdateForm, \
    SessionQuoteAlternativeCreateForm, SessionQuoteUpdate2Form, \
    UserPreferencesUpdateForm, ImageSelectionAutoCreateForm, CustomAuthenticationForm
from lumina.mail import send_email, send_email_for_session_quote


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
        ImageSelection.objects.image_selections_pending_to_upload_full_quality_images(
            request.user)
    image_selection_with_pending_uploads_count = image_selection_with_pending_uploads.count()

    if image_selection_with_pending_uploads_count:
        messages.warning(request,
                         'Hay {} solicitud{} de selección de fotos '
                         'esperando que se suban la fotografías en calidad total'
                         ''.format(image_selection_with_pending_uploads_count,
                                   '' if image_selection_with_pending_uploads_count == 1 else 'es'))

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

    with open(full_filename) as f:
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
    zip_buffer = StringIO()
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


@cache_control(private=True)
def shared_session_by_email_image_thumb_64x64(request, random_hash, image_id):
    shared_album = SharedSessionByEmail.objects.get(random_hash=random_hash)
    return _image_thumb(request, shared_album.get_image_from_session(image_id), 64)


@cache_control(private=True)
def shared_session_by_email_image_download(request, random_hash, image_id):
    shared_album = SharedSessionByEmail.objects.get(random_hash=random_hash)
    image = shared_album.get_image_from_session(image_id)
    return _image_download(request, image)


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
        return ImageSelection.objects.image_selections_pending_to_upload_full_quality_images(
            self.request.user)

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionWithPendingUploadsListView, self).get_context_data(**kwargs)
        context['for_pending_uploads'] = True
        return context


class ImageSelectionUploadPendingView(DetailView):
    model = ImageSelection
    template_name = 'lumina/imageselection_upload_pending.html'

    def get_queryset(self):
        return ImageSelection.objects.image_selections_pending_to_upload_full_quality_images(
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


# ===============================================================================
# Session
# ===============================================================================

class SessionListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Session

    def _archived(self):
        return self.request.REQUEST.get('archived', '0') == '1'

    def get_context_data(self, **kwargs):
        context = super(SessionListView, self).get_context_data(**kwargs)
        context['list_archived'] = self._archived()
        return context

    def get_queryset(self):
        qs = Session.objects.visible_sessions(self.request.user)
        if self._archived():
            qs = qs.filter(archived=True)
        else:
            # qs.filter(archived=False) -> DOES NOT WORKS
            # at least with sqlite
            qs = qs.exclude(archived=True)
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

        # thumb_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQA(...)AP/2Q=="
        assert thumb_base64.startswith(PREFIX)
        thumb_base64 = thumb_base64[len(PREFIX):]
        thumb_contents = base64.decodestring(thumb_base64)

        new_image = Image(session=session, studio=request.user.studio,
                          thumbnail_content_type='image/jpg')

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


# ===============================================================================
# Image
# ===============================================================================

class ImageListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Image

    def get_queryset(self):
        return Image.objects.visible_images(self.request.user)


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image
    form_class = ImageCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        return reverse('session_detail', args=[self.object.session.pk])

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio

        #    *** before super().form_valid()
        #    (Pdb) form.instance.image.name
        #    u'estado-del-arte.odt'
        #    *** after super().form_valid()
        #    (Pdb) form.instance.image.name
        #    u'images/2013/06/02/estado-del-arte_2.odt'
        form.instance.set_original_filename(form.instance.image.name)

        #    *** befor and after super().form_valid() this works
        #    (Pdb) form.instance.image.size
        #    77052
        form.instance.size = form.instance.image.size

        # FIXME: is NOT safe to trust the content type reported by the user
        #    *** befor super().form_valid() this works
        #    (Pdb) form.files['image'].content_type
        #    u'application/vnd.oasis.opendocument.text'
        form.instance.set_content_type(form.files['image'].content_type)

        ret = super(ImageCreateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue creada correctamente')

        #    *** after super().form_valid() `form.instance.image.name` has the
        #        filename from the filesystem, which WILL BE DIFFERENT from the
        #        original filename on the user's computer
        #    (Pdb) form.instance.image.name
        #    u'images/2013/06/02/estado-del-arte_2.odt'

        return ret

    def get_initial(self):
        initial = super(ImageCreateView, self).get_initial()
        if 'id_session' in self.request.GET:
            initial.update({
                'session': self.request.GET['id_session'],
            })
        return initial

    def get_context_data(self, **kwargs):
        context = super(ImageCreateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()
        context['title'] = "Agregar imagen"
        context['submit_label'] = "Agregar"
        context['multipart'] = True
        return context


class ImageUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Image
    form_class = ImageUpdateForm
    template_name = 'lumina/image_update_form.html'

    #    def get_context_data(self, **kwargs):
    #        context = super(ImageUpdateView, self).get_context_data(**kwargs)
    #        context.update({'menu_image_update_flag': 'active'})
    #        return context

    def get_queryset(self):
        return self.request.user.studio.image_set.all()

    def form_valid(self, form):
        ret = super(ImageUpdateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue actualizada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(ImageUpdateView, self).get_context_data(**kwargs)
        context['form'].fields['session'].queryset = self.request.user.studio.session_set.all()
        return context


# ===============================================================================
# Customer
# ===============================================================================

class CustomerListView(ListView):
    model = Customer
    template_name = 'lumina/customer_list.html'

    def get_queryset(self):
        return self.request.user.all_my_customers()


class CustomerCreateView(CreateView):
    model = Customer
    form_class = CustomerCreateForm
    template_name = 'lumina/base_create_update_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super(CustomerCreateView, self).form_valid(form)
        messages.success(self.request, 'El cliente fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(CustomerCreateView, self).get_context_data(**kwargs)
        context['title'] = "Agregar cliente"
        context['submit_label'] = "Agregar"
        return context


class CustomerUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Customer
    form_class = CustomerUpdateForm
    template_name = 'lumina/base_create_update_form.html'
    success_url = reverse_lazy('customer_list')

    def get_queryset(self):
        return self.request.user.all_my_customers()

    def form_valid(self, form):
        ret = super(CustomerUpdateView, self).form_valid(form)
        messages.success(self.request, 'El cliente fue actualizado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(CustomerUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar cliente"
        context['submit_label'] = "Actualizar"
        return context


# ===============================================================================
# User
# ===============================================================================

class UserListView(ListView):
    model = LuminaUser
    template_name = 'lumina/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        customer_id = int(self.kwargs['customer_id'])
        context['customer'] = self.request.user.all_my_customers().get(pk=customer_id)
        return context

    def get_queryset(self):
        customer_id = int(self.kwargs['customer_id'])
        return self.request.user.get_users_of_customer(customer_id)


class UserCreateView(CreateView):
    model = LuminaUser
    form_class = UserCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        return reverse('customer_user_list', kwargs={'customer_id': self.kwargs['customer_id']})

    def form_valid(self, form):
        customer = self.request.user.all_my_customers().get(pk=self.kwargs['customer_id'])
        form.instance.user_for_customer = customer
        form.instance.user_type = LuminaUser.CUSTOMER
        ret = super(UserCreateView, self).form_valid(form)

        # Set the password
        new_user = LuminaUser.objects.get(pk=form.instance.id)
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request, 'El cliente fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear usuario"
        context['submit_label'] = "Crear"
        return context


class UserUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = LuminaUser
    form_class = UserUpdateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        customer = self.get_object().user_for_customer
        return reverse('customer_user_list', kwargs={'customer_id': customer.id})

    def get_queryset(self):
        return self.request.user.get_all_users()

    def form_valid(self, form):
        ret = super(UserUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = LuminaUser.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request, 'El cliente fue actualizado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(UserUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar usuario"
        context['submit_label'] = "Actualizar"
        return context


# ===============================================================================
# UserPreference
# ===============================================================================

class UserPreferenceUpdateView(UpdateView):
    model = UserPreferences
    form_class = UserPreferencesUpdateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_success_url(self):
        # TODO: fix this
        return reverse('home')

    def form_valid(self, form):
        ret = super(UserPreferenceUpdateView, self).form_valid(form)
        messages.success(self.request, 'Las preferencias fueron guardados correctamente')
        return ret

    def get_queryset(self):
        return UserPreferences.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super(UserPreferenceUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar preferencias"
        context['submit_label'] = "Actualizar"
        return context


# ===============================================================================
# SessionQuote
# ===============================================================================

class SessionQuoteCreateUpdateMixin():
    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers


class SessionQuoteCreateView(CreateView, SessionQuoteCreateUpdateMixin):
    model = SessionQuote
    form_class = SessionQuoteCreateForm
    template_name = 'lumina/sessionquote_create.html'

    def get_form(self, form_class):
        form = super(SessionQuoteCreateView, self).get_form(form_class)
        self._setup_form(form)
        form.fields['terms'].initial = self.request.user.studio.default_terms or ''
        return form

    def form_valid(self, form):
        form.instance.studio = self.request.user.studio
        ret = super(SessionQuoteCreateView, self).form_valid(form)
        messages.success(self.request, 'El presupuesto fue creado correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear presupuesto"
        context['submit_label'] = "Crear"
        return context

    def get_success_url(self):
        return reverse('quote_detail', args=[self.object.id])


class SessionQuoteUpdateView(UpdateView, SessionQuoteCreateUpdateMixin):
    """
    Allows the photographer modify a Quote.

    The SessionQuote instance is fully modificable ONLY if in state STATUS_QUOTING.
    If STATUS_WAITING_CUSTOMER_RESPONSE or STATUS_ACCEPTED, only the alternatives
    are modificables.
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = SessionQuote
    # form_class = SessionQuoteUpdateForm
    template_name = 'lumina/sessionquote_update_form.html'

    def get_form_class(self):
        if self.object.status == SessionQuote.STATUS_QUOTING:
            # modificable
            return SessionQuoteUpdateForm
        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            # ro
            return SessionQuoteUpdate2Form
        elif self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            # ro
            return SessionQuoteUpdate2Form
        else:
            raise SuspiciousOperation()

    def get_form(self, form_class):
        form = super(SessionQuoteUpdateView, self).get_form(form_class)
        if self.object.status == SessionQuote.STATUS_QUOTING:
            self._setup_form(form)
        return form

    def get_queryset(self):
        return SessionQuote.objects.modificable_sessionquote(self.request.user)

    def form_valid(self, form):
        # from Django docs:
        # > This method is called when valid form data has been POSTed.
        # > It should return an HttpResponse.

        if self.object.status == SessionQuote.STATUS_QUOTING:
            if 'default_button' in self.request.POST:  # Submit for 'Update'
                return super(SessionQuoteUpdateView, self).form_valid(form)

        delete_alternative = [k for k in list(self.request.POST.keys())
                              if k.startswith('delete_alternative_')]

        if delete_alternative:
            assert len(delete_alternative) == 1
            alt_to_delete = delete_alternative[0].split('_')[2]
            to_delete = self.object.quote_alternatives.get(pk=int(alt_to_delete))
            to_delete.delete()
            # This delete is super-safe because the foreign-key is set to 'PROTECT'.
            # If the customer changes his/her alternative to the one being deleted,
            # the DB will refuse this delete automatically :-D
            return HttpResponseRedirect(reverse('quote_update', args=[self.object.id]))

        # FIXME: add an error messages and do a redirect instead of this
        raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteUpdateView, self).get_context_data(**kwargs)
        context['title'] = "Actualizar presupuesto"

        if self.object.status == SessionQuote.STATUS_QUOTING:
            context['submit_label'] = "Actualizar"
            context['full_edit'] = True
        else:
            context['full_edit'] = False

        buttons = context.get('extra_buttons', [])
        buttons.append({'link_url': reverse('quote_detail', args=[self.object.id]),
                        'link_label': "Volver", })
        context['extra_buttons'] = buttons
        _put_session_statuses_in_context(context)
        return context

    def get_success_url(self):
        return reverse('quote_detail', args=[self.object.id])


class SessionQuoteListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = SessionQuote
    filter = ''

    def get_queryset(self):
        qs = SessionQuote.objects.visible_sessionquote(self.request.user)
        if self.filter == 'pending_for_customer':
            qs = qs.filter(status=SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)
        return qs.order_by('customer__name', 'id')


class SessionQuoteDetailView(DetailView):
    """
    This view allows the users (both photographers & customers)
    to see the Quote and, for the customer, accept or reject.

    This is kind a 'read-only' view... The 'read-write' view is SessionQuoteAlternativeSelectView
    """
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = SessionQuote

    def get_queryset(self):
        return SessionQuote.objects.visible_sessionquote(self.request.user)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        if 'button_update' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        elif 'button_confirm' in request.POST:
            quote.confirm(request.user)
            messages.success(self.request,
                             'El presupuesto fue confirmado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_go_to_choose_quote' in request.POST:
            return HttpResponseRedirect(reverse('quote_choose_alternative', args=[quote.id]))

        elif 'button_cancel' in request.POST:
            quote.cancel(request.user)
            messages.success(self.request,
                             'El presupuesto fue cancelado')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail',
                                                args=[quote.id]))

        elif 'button_cancel_and_new_version' in request.POST:
            # FIXME: implement this!
            messages.error(self.request, "La creacion de nuevas versiones "
                                         "de presupuestos todavia no esta implementada.")
            return HttpResponseRedirect(reverse('home'))

        elif 'button_archive_quote' in request.POST:
            # FIXME: implement this!
            messages.error(self.request, "El archivado "
                                         "de presupuestos todavia no esta implementado.")
            return HttpResponseRedirect(reverse('home'))

        elif 'button_update_quote_alternatives' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        elif 'button_create_session' in request.POST:
            new_session = quote.create_session(request.user)
            return HttpResponseRedirect(reverse('session_update', args=[new_session.id]))

        else:
            raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteDetailView, self).get_context_data(**kwargs)
        buttons = []

        if self.object.status == SessionQuote.STATUS_QUOTING:
            # The photographer did not finished the Quote
            if self.request.user.is_for_customer():
                # The customer shouln't see this Quote
                raise SuspiciousOperation()
            else:
                buttons.append({'name': 'button_update',
                                'submit_label': "Editar", })
                buttons.append({'name': 'button_confirm',
                                'submit_label': "Confirmar", 'confirm': True, })
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })

        elif self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            # Waiting for customer accept()/reject().
            # Photographer always can cancel()
            if self.request.user.is_for_customer():
                buttons.append({'name': 'button_go_to_choose_quote',
                                'submit_label': "Respdoner presupuesto (aceptar/rechazar)", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                buttons.append({'name': 'button_cancel_and_new_version',
                                'submit_label': "Cancelar presupuesto y crear nueva versión",
                                'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })

        elif self.object.status == SessionQuote.STATUS_REJECTED:
            if self.request.user.is_for_customer():
                pass
            else:
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            if self.request.user.is_for_customer():
                # show button to change alternatives ONLY if exists more alternatives
                if self.object.get_valid_alternatives().count() > 0:
                    buttons.append({'name': 'button_go_to_choose_quote',
                                    'submit_label': "Cambiar alternativa de presupuesto", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                buttons.append({'name': 'button_cancel_and_new_version',
                                'submit_label': "Cancelar presupuesto y crear nueva versión",
                                'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })
                if self.object.session is None:
                    buttons.append({'name': 'button_create_session',
                                    'submit_label': "Crear sesión", })

        elif self.object.status == SessionQuote.STATUS_CANCELED:
            # Canceled
            if self.request.user.is_for_customer():
                pass
            else:
                buttons.append({'name': 'button_archive_quote',
                                'submit_label': "Archivar", })

        else:
            raise Exception("Invalid 'status': {}".format(self.object.status))

        context['selected_quote'] = self.object.get_selected_quote()
        context['extra_buttons'] = buttons
        _put_session_statuses_in_context(context)

        return context


class SessionQuoteAlternativeSelectView(DetailView):
    """
    This view allows the select a quote alternative to customers.

    This is kind a 'read-write' view... The 'read-only' view is SessionQuoteDetailView
    """
    model = SessionQuote
    template_name = 'lumina/sessionquote_detail_choose_alternative.html'

    def get_queryset(self):
        # TODO: we should not use `visible_sessionquote()`
        return SessionQuote.objects.visible_sessionquote(self.request.user)

    def post(self, request, *args, **kwargs):
        quote = self.get_object()
        if 'button_accept' in request.POST:
            if 'accept_terms' not in request.POST:
                messages.error(self.request, 'Debe aceptar las condiciones')
                return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))
            alternative = request.POST['selected_quote']

            if alternative == '0':
                params = None
            else:
                alt_quantity, alt_cost = alternative.split('_')
                params = [int(alt_quantity), decimal.Decimal(alt_cost)]

            if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
                quote.accept(request.user, params)
            elif quote.status == SessionQuote.STATUS_ACCEPTED:
                quote.update_quote_alternative(request.user, params)
            else:
                raise SuspiciousOperation()

            messages.success(self.request,
                             'El presupuesto fue aceptado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail', args=[quote.id]))

        elif 'button_reject' in request.POST:
            quote.reject(request.user)
            messages.success(self.request,
                             'El presupuesto fue rechazado correctamente')
            send_email_for_session_quote(quote, self.request.user, self.request)
            return HttpResponseRedirect(reverse('quote_detail',
                                                args=[quote.id]))

        else:
            raise SuspiciousOperation()

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteAlternativeSelectView, self).get_context_data(**kwargs)

        context['available_alternatives'] = self.object.get_valid_alternatives()

        if not self.request.user.is_for_customer():
            raise Exception("The user is not a customer! User: {}".format(self.request.user))

        if self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            pass

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            # Accepted or rejected -> photographer always can cancel()
            selected_quote = self.object.get_selected_quote()
            assert selected_quote >= 0
            context['selected_quote'] = selected_quote

        else:
            raise Exception("Invalid 'status': {}".format(self.object.status))

        _put_session_statuses_in_context(context)

        return context


# ------------------------------------------------------------------------------------------

class SessionQuoteAlternativeCreateView(CreateView):
    model = SessionQuoteAlternative
    form_class = SessionQuoteAlternativeCreateForm
    template_name = 'lumina/sessionquote_alternative_create_update.html'

    def get_initial(self):
        initial = super(SessionQuoteAlternativeCreateView, self).get_initial()
        session_quote_id = self.kwargs['session_quote_id']
        initial.update({'session_quote': SessionQuote.objects.get(pk=session_quote_id)})
        return initial

    def form_valid(self, form):
        session_quote_id = self.kwargs['session_quote_id']
        session_quote = SessionQuote.objects.get(pk=session_quote_id)
        # check unique
        qs = session_quote.quote_alternatives
        if qs.filter(image_quantity=form.instance.image_quantity).count() != 0:
            messages.error(self.request,
                           'Ya existe una alternativa para la cantidad de fotos ingresada')
            return self.render_to_response(self.get_context_data(form=form))

        form.instance.session_quote = session_quote
        ret = super(SessionQuoteAlternativeCreateView, self).form_valid(form)
        messages.success(self.request, 'La alternativa fue creada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteAlternativeCreateView, self).get_context_data(**kwargs)
        context['title'] = "Crear alternativa de presupuesto"
        context['submit_label'] = "Crear"

        buttons = context.get('extra_buttons', [])
        buttons.append({'link_url': reverse('quote_update',
                                            args=[self.kwargs['session_quote_id']]),
                        'link_label': "Volver", })
        context['extra_buttons'] = buttons
        return context

    def get_success_url(self):
        return reverse('quote_update', args=[self.kwargs['session_quote_id']])
