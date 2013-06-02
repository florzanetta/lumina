# Create your views here.

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from lumina.models import Image, Album
from lumina.pil_utils import generate_thumbnail
from lumina.forms import ImageCreateForm, ImageUpdateForm, AlbumCreateForm,\
    AlbumUpdateForm

#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


@login_required
def image_thumb_64x64(request, image_id):
    return image_thumb(request, image_id, 64)


@login_required
def image_thumb(request, image_id, max_size=None):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    try:
        thumb = generate_thumbnail(image, max_size)
        return HttpResponse(thumb, content_type='image/jpg')
    except IOError:
        return HttpResponseRedirect('/static/album-icon-64x64.png')


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
        return super(AlbumCreateView, self).form_valid(form)


class AlbumUpdateView(UpdateView):

    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Album
    form_class = AlbumUpdateForm
    template_name = 'lumina/album_update_form.html'


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
        return super(ImageCreateView, self).form_valid(form)

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
