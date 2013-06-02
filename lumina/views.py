# Create your views here.

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required

from lumina.models import Image, Album
from lumina.pil_utils import generate_thumbnail

#
# List of generic CBV:
#  - https://docs.djangoproject.com/en/1.5/ref/class-based-views/
#


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


@login_required
def image_thumb_64x64(request, image_id):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return HttpResponse(generate_thumbnail(image, max_size=64),
        content_type='image/jpg')


@login_required
def image_thumb(request, image_id):
    image = Image.objects.for_user(request.user).get(pk=image_id)
    return HttpResponse(generate_thumbnail(image), content_type='image/jpg')


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
    model = Image


class ImageUpdateView(UpdateView):
    # https://docs.djangoproject.com/en/1.5/ref/class-based-views/generic-editing/#updateview
    model = Image

    #    def get_context_data(self, **kwargs):
    #        context = super(ImageUpdateView, self).get_context_data(**kwargs)
    #        context.update({'menu_image_update_flag': 'active'})
    #        return context
