# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from lumina.models import Image


def home(request):
    ctx = {
        'images': Image.objects.all_from_user(request.user),
    }
    return render_to_response('lumina/index.html', ctx,
        context_instance=RequestContext(request))
