import datetime
import json

from django.http.response import HttpResponse


def ping(request):
    response_data = {
        'status': 'ok',
        'server_date_str': str(datetime.datetime.now()),
    }

    if request.user.is_anonymous():
        response_data['username'] = ''
    else:
        response_data['username'] = request.user.username

    return HttpResponse(json.dumps(response_data), content_type="application/json")
