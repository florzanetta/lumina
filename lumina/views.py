# Create your views here.

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.servers.basehttp import FileWrapper

from lumina.models import Image, Album, SharedAlbum
from lumina.pil_utils import generate_thumbnail
from lumina.forms import ImageCreateForm, ImageUpdateForm, AlbumCreateForm, \
    AlbumUpdateForm
from django.core.files.storage import default_storage
import mimetypes
import os

#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#

# TODO: send cache headers


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


def _image_thumb(request, image, max_size=None):
    try:
        thumb = generate_thumbnail(image, max_size)
        return HttpResponse(thumb, content_type='image/jpg')
    except IOError:
        return HttpResponseRedirect('/static/unknown-icon-64x64.png')


@login_required
def image_thumb_64x64(request, image_id):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


@login_required
def image_thumb(request, image_id, max_size=None):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return _image_thumb(request, image, 64)


#===============================================================================
# SharedAlbum
#===============================================================================

def shared_album_view(request, random_hash):
    shared_album = SharedAlbum.objects.get(random_hash=random_hash)
    return render_to_response('lumina/sharedalbum_view.html', {'object': shared_album, },
        context_instance=RequestContext(request))


def shared_album_image_thumb_64x64(request, random_hash, image_id):
    shared_album = SharedAlbum.objects.get(random_hash=random_hash)
    return _image_thumb(request, shared_album.get_image_from_album(image_id), 64)


def shared_album_image_download(request, random_hash, image_id):
    shared_album = SharedAlbum.objects.get(random_hash=random_hash)
    image = shared_album.get_image_from_album(image_id)
    full_filename = default_storage.path(image.image.path)
    filename_to_user = os.path.basename(full_filename)
    filesize = os.path.getsize(full_filename)
    content_type = mimetypes.guess_type(full_filename)[0]

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


#===============================================================================
# Album
#===============================================================================

class AlbumListView(ListView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/#django.views.generic.list.ListView @IgnorePep8
    model = Album

    def get_queryset(self):
        return Album.objects.for_user(self.request.user)


class AlbumDetailView(DetailView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/#django.views.generic.detail.DetailView @IgnorePep8
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
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-display/#django.views.generic.list.ListView @IgnorePep8
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
        ret = super(ImageCreateView, self).form_valid(form)
        messages.success(self.request, 'La imagen fue creada correctamente')
        return ret

    def get_initial(self):
        initial = super(ImageCreateView, self).get_initial()
        if 'id_album' in self.request.GET:
            initial.update({
                'album': self.request.GET['id_album'],
            })
        return initial


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
