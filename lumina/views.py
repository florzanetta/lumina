# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView

from lumina.models import Image


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


class ImageListView(ListView):
    model = Image

    def get_queryset(self):
        return Image.objects.all_from_user(self.request.user)


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image


class ImageUpdateView(UpdateView):
    model = Image
