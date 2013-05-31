# Create your views here.

from cStringIO import StringIO
from PIL import  Image as PilImage

from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.http.response import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage

from lumina.models import Image


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


@login_required
def image_thumb(request, image_id):
    img = PilImage.open(default_storage.path(
        Image.objects.all_from_user(request.user).get(pk=image_id).image.path))
    img.thumbnail((100, 100,), PilImage.ANTIALIAS)
    output_file = StringIO()
    img.save(output_file, "JPEG")
    return HttpResponse(output_file.getvalue(), content_type='image/jpg')


class ImageListView(ListView):
    model = Image

    def get_queryset(self):
        return Image.objects.all_from_user(self.request.user)


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image


class ImageUpdateView(UpdateView):
    model = Image

    #    def get_context_data(self, **kwargs):
    #        context = super(ImageUpdateView, self).get_context_data(**kwargs)
    #        context.update({'menu_image_update_flag': 'active'})
    #        return context
