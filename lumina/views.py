# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from lumina.models import Image


def home(request):
    return render_to_response('lumina/index.html', {},
        context_instance=RequestContext(request))


@login_required
def images_list(request):
    ctx = {
        'images': Image.objects.all_from_user(request.user),
    }
    return render_to_response('lumina/images_list.html', ctx,
        context_instance=RequestContext(request))
