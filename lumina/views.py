# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required

from lumina.models import Image


@login_required
def home(request):
    ctx = {
        'images': Image.objects.all_from_user(request.user),
    }
    return render_to_response('lumina/index.html', ctx,
        context_instance=RequestContext(request))
