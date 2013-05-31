# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView, UpdateView

from lumina.models import Image


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


@login_required
def images_list(request):
    ctx = {
        'images': Image.objects.all_from_user(request.user),
    }
    return render_to_response('lumina/image_list.html', ctx,
        context_instance=RequestContext(request))


class ImageCreateView(CreateView):
    # https://docs.djangoproject.com/en/1.5/topics/class-based-views/generic-editing/
    model = Image


class ImageUpdateView(UpdateView):
    model = Image
