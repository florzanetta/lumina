# -*- coding: utf-8 -*-

import base64
import json
import logging
import os
import uuid
import decimal

import mailer

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
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
    SharedSessionByEmail, ImageSelection, SessionQuote, SessionQuoteAlternative
from lumina.forms import SessionCreateForm, SessionUpdateForm, \
    CustomerCreateForm, CustomerUpdateForm, UserCreateForm, UserUpdateForm, \
    SharedSessionByEmailCreateForm, ImageCreateForm, ImageUpdateForm, \
    ImageSelectionCreateForm, SessionQuoteCreateForm, SessionQuoteUpdateForm, \
    SessionQuoteAlternativeCreateForm, SessionQuoteUpdate2Form


#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#
# Cache:
#  - https://docs.djangoproject.com/en/1.5/topics/cache/#controlling-cache-using-other-headers
#

logger = logging.getLogger(__name__)


def send_emails(subject, to_email_list, body):
    logger.info("Sending email '{}' to '{}'".format(
        subject, to_email_list))
    from_email = "Lumina <notifications@lumina-photo.com.ar>"
    try:
        mailer.send_mail(subject, body, from_email, to_email_list, fail_silently=False)
        logger.info("Email to %s, with subject '%s' queued", to_email_list, subject)
    except:
        logger.exception("Couldn't queue email to %s", to_email_list)
        pass


def send_email(subject, to_email, body):
    return send_emails(subject, [to_email], body)


def send_email_for_session_quote(quote, user, request):
    """
    Send an email informing the change of status of SessionQuote.
    The new status is taken from quote.status
    """
    link = request.build_absolute_uri(reverse('quote_detail',
                                              args=[quote.id]))

    if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
        # send to customer
        subject = "Ud. posee un nuevo presupuesto"
        to_email_list = [u.email for u in quote.customer.users.all()]
        body = ("Ud. posee un nuevo presupuesto.\n"
                "Para verlo, acceda a {}.\n"
                "".format(link))
        send_emails(subject, to_email_list, body)

        # send to photographers
        subject = "Se ha enviado un presupuesto"
        to_email_list = [u.email for u in quote.studio.photographers.all()]
        body = ("Se ha enviado un presupuesto.\n"
                "Cliente: {}.\n"
                "Enviado por: {}.\n"
                "Para verlo, acceda a {}."
                "".format(quote.customer, user, link))
        send_emails(subject, to_email_list, body)

    elif quote.status == SessionQuote.STATUS_ACCEPTED:
        # send to customer
        subject = "Se ha aceptado un presupuesto"
        to_email_list = [u.email for u in quote.customer.users.all()]
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list, body)

        # send to photographers
        subject = "Un cliente ha aceptado un presupuesto"
        to_email_list = [u.email for u in quote.studio.photographers.all()]
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list, body)

    elif quote.status == SessionQuote.STATUS_REJECTED:
        # send to customer
        subject = "Se ha rechazado un presupuesto"
        to_email_list = [u.email for u in quote.customer.users.all()]
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list, body)

        # send to photographers
        subject = "Un cliente ha rechazado un presupuesto"
        to_email_list = [u.email for u in quote.studio.photographers.all()]
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list, body)

    elif quote.status == SessionQuote.STATUS_CANCELED:
        # send to photographers
        subject = "Se ha cancelado un presupuesto"
        to_email_list = [u.email for u in quote.studio.photographers.all()]
        body = ("Se ha cancelado un presupuesto.\n"
                "El presupuesto fue cancelado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list, body)

    elif quote.status == SessionQuote.STATUS_QUOTING:
        pass

    else:
        logger.error("send_email_for_session_quote(): Invalid quote.status: '%s'",
                     quote.status)
        return


def _photographer_home(request):
    ctx = {
        'session_count': Session.objects.visible_sessions(request.user).count(),
        'image_count': Image.objects.visible_images(request.user).count(),
        'shared_session_via_email_count':
        request.user.all_my_shared_sessions_by_email().count()
    }
    return render_to_response(
        'lumina/index_photographer.html', ctx,
        context_instance=RequestContext(request))


def _customer_home(request):
    ctx = {
        'quotes_pending_count': SessionQuote.objects.get_waiting_for_customer_response(
            request.user).count(),
        'session_count': Session.objects.visible_sessions(request.user).count(),
        'image_selection_pending_count': ImageSelection.objects.pending_image_selections(
            request.user).count(),
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
    # 'auth_providers': request.user.social_auth.get_providers(),
    if not request.user.is_authenticated():
        # ----- Anonymous
        ctx = {}
        return render_to_response(
            'lumina/index_anonymous.html', ctx,
            context_instance=RequestContext(request))

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
    raise(ObjectDoesNotExist())


@login_required
@cache_control(private=True)
def check_500(request):
    logger.info("Raising Exception()")
    raise(Exception())


@login_required
@cache_control(private=True)
def check_403(request):
    logger.info("Raising PermissionDenied()")
    raise(PermissionDenied())


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


#===============================================================================
# SharedSessionByEmail (ex: SharedAlbum)
#===============================================================================

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


#===============================================================================
# ImageSelection
#===============================================================================

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
        message = u"Tiene una nueva solicitud para seleccionar fotografías.\n" + \
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
            raise(SuspiciousOperation("Invalid ids: {}".format(','.join(invalid_ids))))

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
                raise(SuspiciousOperation())
            ctx['images_to_show'] = image_selection.session.image_set.all()
            ctx['selected_images'] = image_selection.selected_images.all()

        elif self.request.user.is_for_customer():
            # Show only selected images to customer
            if image_selection.session.customer != self.request.user.user_for_customer:
                raise(SuspiciousOperation())
            ctx['images_to_show'] = image_selection.selected_images.all()

        else:
            raise(SuspiciousOperation())

        return ctx


#===============================================================================
# Session
#===============================================================================

class SessionListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Session

    def get_queryset(self):
        qs = Session.objects.visible_sessions(self.request.user)
        return qs.order_by('customer__name', 'name')


class SessionDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = Session

    def get_queryset(self):
        return Session.objects.visible_sessions(self.request.user)


class SessionCreateUpdateMixin():

    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers
        form.fields['shared_with'].queryset = qs_customers
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
        if not key in request.POST:
            break
        img_count += 1
        index += 1

        thumb_base64 = request.POST[key]
        filename = request.POST[key + '_filename']

        # thumb_base64 = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQA(...)AP/2Q=="
        assert thumb_base64.startswith(PREFIX)
        thumb_base64 = thumb_base64[len(PREFIX):]
        thumb_contents = base64.decodestring(thumb_base64)

        new_image = Image(
            session=session, studio=request.user.studio, content_type='image/jpg',
            original_filename='thumb_' + filename)

        new_image.size = len(thumb_contents)
        new_image.image.save('thumb_' + filename, ContentFile(thumb_contents))
        new_image.save()

    response_data = {
        'img_count': img_count,
        'status': 'ok',
        'redirect': reverse('session_detail', args=[session.id]),
    }
    return HttpResponse(json.dumps(response_data), content_type="application/json")


#===============================================================================
# Image
#===============================================================================

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


#===============================================================================
# Customer
#===============================================================================

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


#===============================================================================
# User
#===============================================================================

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


#===============================================================================
# User
#===============================================================================

class SessionQuoteCreateUpdateMixin():

    def _setup_form(self, form):
        qs_customers = self.request.user.all_my_customers()
        form.fields['customer'].queryset = qs_customers


class SessionQuoteCreateView(CreateView, SessionQuoteCreateUpdateMixin):
    model = SessionQuote
    form_class = SessionQuoteCreateForm
    template_name = 'lumina/base_create_update_form.html'

    def get_form(self, form_class):
        form = super(SessionQuoteCreateView, self).get_form(form_class)
        self._setup_form(form)
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
            raise(SuspiciousOperation())

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

        delete_alternative = [k for k in self.request.POST.keys()
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
        raise(SuspiciousOperation())

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

    def get_queryset(self):
        qs = SessionQuote.objects.visible_sessionquote(self.request.user)
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

        elif 'button_update_quote_alternatives' in request.POST:
            return HttpResponseRedirect(reverse('quote_update', args=[quote.id]))

        else:
            raise(SuspiciousOperation())

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteDetailView, self).get_context_data(**kwargs)
        buttons = []

        if self.object.status == SessionQuote.STATUS_QUOTING:
            # The photographer did not finished the Quote
            if self.request.user.is_for_customer():
                # The customer shouln't see this Quote
                raise(SuspiciousOperation())
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
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })

        elif self.object.status == SessionQuote.STATUS_REJECTED:
            pass

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            if self.request.user.is_for_customer():
                buttons.append({'name': 'button_go_to_choose_quote',
                                'submit_label': "Cambiar alternativa de presupuesto", })
            else:
                buttons.append({'name': 'button_cancel',
                                'submit_label': "Cancelar presupuesto", 'confirm': True, })
                buttons.append({'name': 'button_update_quote_alternatives',
                                'submit_label': "Editar presup. alternativos", })

        elif self.object.status == SessionQuote.STATUS_CANCELED:
            # Canceled
            pass

        else:
            raise(Exception("Invalid 'status': {}".format(self.object.status)))

        context['selected_quote'] = self.object.get_selected_quote
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
                raise(SuspiciousOperation())

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
            raise(SuspiciousOperation())

    def get_context_data(self, **kwargs):
        context = super(SessionQuoteAlternativeSelectView, self).get_context_data(**kwargs)

        context['available_alternatives'] = self.object.get_valid_alternatives()

        if not self.request.user.is_for_customer():
            raise(Exception("The user is not a customer! User: {}".format(self.request.user)))

        if self.object.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
            pass

        elif self.object.status == SessionQuote.STATUS_ACCEPTED:
            # Accepted or rejected -> photographer always can cancel()
            selected_quote = self.object.get_selected_quote()
            assert selected_quote >= 0
            context['selected_quote'] = selected_quote

        else:
            raise(Exception("Invalid 'status': {}".format(self.object.status)))

        _put_session_statuses_in_context(context)

        return context


# ------------------------------------------------------------------------------------------

class SessionQuoteAlternativeCreateView(CreateView):
    model = SessionQuoteAlternative
    form_class = SessionQuoteAlternativeCreateForm
    template_name = 'lumina/base_create_update_form.html'

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
