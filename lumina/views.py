# -*- coding: utf-8 -*-

import os
import uuid
import logging

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

from lumina.models import Image, Album, SharedAlbum, \
    ImageSelection, LuminaUser
from lumina.pil_utils import generate_thumbnail
from lumina.forms import ImageCreateForm, ImageUpdateForm, AlbumCreateForm, \
    AlbumUpdateForm, SharedAlbumCreateForm, CustomerCreateForm, \
    CustomerUpdateForm, ImageSelectionCreateForm


#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#
# Cache:
#  - https://docs.djangoproject.com/en/1.5/topics/cache/#controlling-cache-using-other-headers
#

logger = logging.getLogger(__name__)


def send_email(subject, to_email, body):
    logger.info("Sending email '{}' to '{}'".format(
        subject, to_email))
    from_email = "Lumina <notifications@lumina-photo.com.ar>"
    try:
        mailer.send_mail(subject, body, from_email, [to_email], fail_silently=False)
        logger.info("Email to %s, with subject '%s' queued", to_email, subject)
    except:
        logger.exception("Couldn't queue email to %s", to_email)
        pass


def home(request):
    if request.user.is_authenticated():
        ctx = {
            'album_count': Album.objects.all_my_albums(request.user).count(),
            'image_count': Image.objects.all_my_images(request.user).count(),
            'shared_album_via_email_count': SharedAlbum.objects.all_my_shares(
                request.user).count(),
            'others_album_count': Album.objects.shared_with_me(request.user).count(),
            'image_selection_pending_count': ImageSelection.objects.pending_image_selections(
                request.user).count(),
#            'auth_providers': request.user.social_auth.get_providers(),
        }
    else:
        ctx = {}
    return render_to_response(
        'lumina/index.html', ctx,
        context_instance=RequestContext(request))


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
    image = Image.objects.all_previsualisable(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_thumb(request, image_id, max_size=None):
    image = Image.objects.all_previsualisable(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_download(request, image_id):
    image = Image.objects.get_for_download(request.user, int(image_id))
    return _image_download(request, image)


#===============================================================================
# SharedAlbum
#===============================================================================

class SharedAlbumAnonymousView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = SharedAlbum
    slug_url_kwarg = 'random_hash'
    slug_field = 'random_hash'
    template_name = 'lumina/sharedalbum_anonymous_view.html'


@cache_control(private=True)
def shared_album_image_thumb_64x64(request, random_hash, image_id):
    shared_album = SharedAlbum.objects.get(random_hash=random_hash)
    return _image_thumb(request, shared_album.get_image_from_album(image_id), 64)


@cache_control(private=True)
def shared_album_image_download(request, random_hash, image_id):
    shared_album = SharedAlbum.objects.get(random_hash=random_hash)
    image = shared_album.get_image_from_album(image_id)
    return _image_download(request, image)


class SharedAlbumCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = SharedAlbum
    form_class = SharedAlbumCreateForm
    template_name = 'lumina/sharedalbum_create_form.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.random_hash = str(uuid.uuid4())
        ret = super(SharedAlbumCreateView, self).form_valid(form)

        subject = "Nuevo album compartido con Ud."
        to_email = form.instance.shared_with
        link = self.request.build_absolute_uri(
            reverse('shared_album_view', args=[form.instance.random_hash]))
        body = "Tiene un nuevo album compartido.\nPara verlo ingrese a {}".format(link)
        send_email(subject, to_email, body)

        messages.success(self.request, 'El album fue compartido correctamente')
        return ret

    def get_initial(self):
        initial = super(SharedAlbumCreateView, self).get_initial()
        if 'id_album' in self.request.GET:
            initial.update({
                'album': self.request.GET['id_album'],
            })
        return initial

    def get_success_url(self):
        return reverse('album_detail', args=[self.object.album.pk])

    def get_context_data(self, **kwargs):
        context = super(SharedAlbumCreateView, self).get_context_data(**kwargs)
        context['form'].fields['album'].queryset = Album.objects.all_my_albums(self.request.user)
        return context


#===============================================================================
# ImageSelection
#===============================================================================

@login_required
@cache_control(private=True)
def imageselection_redirect(request, pk):
    imageselection_id = int(pk)
    imageselection = ImageSelection.objects.all_my_accessible_imageselections(
        request.user).get(id=imageselection_id)
    assert isinstance(imageselection, ImageSelection)

    if imageselection.user == request.user:
        return HttpResponseRedirect(reverse('imageselection_detail',
                                            args=[imageselection_id]))
    else:
        if imageselection.status == ImageSelection.STATUS_IMAGES_SELECTED:
            return HttpResponseRedirect(reverse('imageselection_detail',
                                                args=[imageselection_id]))
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
    template_name = 'lumina/imageselection_create_form.html'

    def get_initial(self):
        initial = super(ImageSelectionCreateView, self).get_initial()
        if 'id_album' in self.request.GET:
            initial.update({
                'album': self.request.GET['id_album'],
            })
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user
        ret = super(ImageSelectionCreateView, self).form_valid(form)

        subject = "Solicitud de seleccion de imagenes"
        to_email = form.instance.customer.email
        link = self.request.build_absolute_uri(
            reverse('album_detail', args=[form.instance.album.id]))
        message = u"Tiene una nueva solicitud para seleccionar fotografías.\n" + \
            "Para verlo ingrese a {}".format(link)
        send_email(subject, to_email, message)

        messages.success(
            self.request, 'La solicitud de seleccion de imagenes '
            'fue creada correctamente.')
        return ret

    def get_success_url(self):
        return reverse('album_detail', args=[self.object.album.pk])

    def get_context_data(self, **kwargs):
        context = super(ImageSelectionCreateView, self).get_context_data(**kwargs)
        context['form'].fields['album'].queryset = Album.objects.all_my_albums(self.request.user)
        customer_qs = self.request.user.all_my_customers()
        context['form'].fields['customer'].queryset = customer_qs
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
        images = image_selection.album.image_set.all()
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
        to_email = image_selection.album.user.email
        link = self.request.build_absolute_uri(
            reverse('imageselection_detail', args=[image_selection.id]))
        body = "El cliente ha seleccionado las imagenes del album.\n" + \
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
        if image_selection.user.id == self.request.user.id:
            # Show all to the photographer
            ctx['images_to_show'] = image_selection.album.image_set.all()
            ctx['selected_images'] = image_selection.selected_images.all()
        elif image_selection.customer.id == self.request.user.id:
            # Show only selected images to customer
            ctx['images_to_show'] = image_selection.selected_images.all()
        else:
            # the requested ImageSelection instance does NOT belong
            # to the photographer neither to the customer!
            raise(SuspiciousOperation())
        return ctx


#===============================================================================
# Album
#===============================================================================

# class SafeAlbumViewMixin(object):
#    def get_queryset(self):
#        return Album.objects.for_user(self.request.user)

class AlbumListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Album

    def get_queryset(self):
        return Album.objects.all_visible(self.request.user)


class AlbumDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = Album

    def get_queryset(self):
        return Album.objects.all_visible(self.request.user)


class AlbumCreateView(CreateView):
    model = Album
    form_class = AlbumCreateForm
    template_name = 'lumina/album_create_form.html'

    def get_form(self, form_class):
        form = super(AlbumCreateView, self).get_form(form_class)
        form.fields['shared_with'].queryset = self.request.user.all_my_customers()
        return form

    def form_valid(self, form):
        form.instance.user = self.request.user
        ret = super(AlbumCreateView, self).form_valid(form)
        messages.success(self.request, 'El album fue creado correctamente')
        return ret


class AlbumUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Album
    form_class = AlbumUpdateForm
    template_name = 'lumina/album_update_form.html'

    def get_form(self, form_class):
        form = super(AlbumUpdateView, self).get_form(form_class)
        form.fields['shared_with'].queryset = self.request.user.all_my_customers()
        return form

    def get_queryset(self):
        return Album.objects.all_my_albums(self.request.user)

    def form_valid(self, form):
        ret = super(AlbumUpdateView, self).form_valid(form)
        messages.success(self.request, 'El album fue actualizado correctamente')
        return ret


#===============================================================================
# Image
#===============================================================================

class ImageListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Image

    def get_queryset(self):
        return Image.objects.all_my_images(self.request.user)


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image
    form_class = ImageCreateForm
    template_name = 'lumina/image_create_form.html'

    def get_success_url(self):
        return reverse('album_detail', args=[self.object.album.pk])

    def form_valid(self, form):
        form.instance.user = self.request.user

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
        if 'id_album' in self.request.GET:
            initial.update({
                'album': self.request.GET['id_album'],
            })
        return initial

    def get_context_data(self, **kwargs):
        context = super(ImageCreateView, self).get_context_data(**kwargs)
        context['form'].fields['album'].queryset = Album.objects.all_my_albums(self.request.user)
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
        return Image.objects.all_my_images(self.request.user)

    def form_valid(self, form):
        ret = super(ImageUpdateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue actualizada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(ImageUpdateView, self).get_context_data(**kwargs)
        context['form'].fields['album'].queryset = Album.objects.all_my_albums(self.request.user)
        return context


#===============================================================================
# LuminaUserProfile
#===============================================================================

class CustomerListView(ListView):
    model = LuminaUser
    template_name = 'lumina/customer_list.html'

    def get_queryset(self):
        return self.request.user.all_my_customers()


class CustomerCreateView(CreateView):
    model = LuminaUser
    form_class = CustomerCreateForm
    template_name = 'lumina/customer_create_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        ret = super(CustomerCreateView, self).form_valid(form)

        # Create the profile module
        new_user = LuminaUser.objects.get(pk=form.instance.id)
        new_user.user_type = LuminaUser.GUEST
        new_user.customer_of = self.request.user

        # Set the password
        new_user.set_password(form['password1'].value())
        new_user.save()

        messages.success(self.request, 'El cliente fue creado correctamente')
        return ret


class CustomerUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = LuminaUser
    form_class = CustomerUpdateForm
    template_name = 'lumina/customer_update_form.html'
    success_url = reverse_lazy('customer_list')

    def get_queryset(self):
        return self.request.user.all_my_customers()

    def form_valid(self, form):
        ret = super(CustomerUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = LuminaUser.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())
            updated_user.save()

        messages.success(self.request, 'El cliente fue actualizado correctamente')
        return ret
