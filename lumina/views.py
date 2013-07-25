# Create your views here.

import os
import uuid
import logging

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
from django.contrib.auth.models import User

from lumina.models import Image, Album, SharedAlbum, LuminaUserProfile
from lumina.pil_utils import generate_thumbnail
from lumina.forms import ImageCreateForm, ImageUpdateForm, AlbumCreateForm, \
    AlbumUpdateForm, SharedAlbumCreateForm, CustomerCreateForm,\
    CustomerUpdateForm


#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#
# Cache:
#  - https://docs.djangoproject.com/en/1.5/topics/cache/#controlling-cache-using-other-headers
#

logger = logging.getLogger(__name__)


def home(request):
    if request.user.is_authenticated():
        ctx = {
            'album_count': Album.objects.for_user(request.user).count(),
            'image_count': Image.objects.for_user(request.user).count(),
            'sharedalbum_count': SharedAlbum.objects.for_user(request.user).count(),
#            'auth_providers': request.user.social_auth.get_providers(),
        }
    else:
        ctx = {}
    return render_to_response(
        'lumina/index.html', ctx,
        context_instance=RequestContext(request))


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
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_thumb(request, image_id, max_size=None):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
@cache_control(private=True)
def image_download(request, image_id):
    image = Image.objects.for_user(request.user).get(pk=image_id)
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
        context['form'].fields['album'].queryset = Album.objects.for_user(self.request.user)
        return context


#===============================================================================
# Album
#===============================================================================

class AlbumListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.list.ListView
    model = Album

    def get_queryset(self):
        return Album.objects.for_user(self.request.user)


class AlbumDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/
    #    #django.views.generic.detail.DetailView
    model = Album

    def get_queryset(self):
        return Album.objects.for_user(self.request.user)


class AlbumCreateView(CreateView):
    model = Album
    form_class = AlbumCreateForm
    template_name = 'lumina/album_create_form.html'

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
        return Image.objects.for_user(self.request.user)


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#createview
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image
    form_class = ImageCreateForm
    template_name = 'lumina/image_create_form.html'

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
        context['form'].fields['album'].queryset = Album.objects.for_user(self.request.user)
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

    def form_valid(self, form):
        ret = super(ImageUpdateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue actualizada correctamente')
        return ret

    def get_context_data(self, **kwargs):
        context = super(ImageUpdateView, self).get_context_data(**kwargs)
        context['form'].fields['album'].queryset = Album.objects.for_user(self.request.user)
        return context


#===============================================================================
# LuminaUserProfile
#===============================================================================

class CustomerListView(ListView):
    model = User
    template_name = 'lumina/customer_list.html'

    def get_queryset(self):
        return User.objects.filter(luminauserprofile__customer_of=self.request.user)


class CustomerCreateView(CreateView):
    model = User
    form_class = CustomerCreateForm
    template_name = 'lumina/customer_create_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        # Set the password
        form.instance.password = form['password1'].value()

        ret = super(CustomerCreateView, self).form_valid(form)

        # Create the profile module
        new_user = User.objects.get(pk=form.instance.id)
        LuminaUserProfile.objects.create(
            user=new_user, user_type=LuminaUserProfile.GUEST, customer_of=self.request.user)

        messages.success(self.request, 'El cliente fue creado correctamente')
        return ret


class CustomerUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = User
    form_class = CustomerUpdateForm
    template_name = 'lumina/customer_update_form.html'
    success_url = reverse_lazy('customer_list')

    def form_valid(self, form):
        #        ret = super(AlbumUpdateView, self).form_valid(form)
        #        messages.success(self.request, 'El album fue actualizado correctamente')
        #        return ret
        ret = super(CustomerUpdateView, self).form_valid(form)

        # Set the password
        if form['password1'].value():
            updated_user = User.objects.get(pk=form.instance.id)
            logger.warn("Changing password of user '%s'", updated_user.username)
            updated_user.set_password(form['password1'].value())

        messages.success(self.request, 'El cliente fue actualizado correctamente')
        return ret
