import datetime
import json

from django.http.response import HttpResponse
from lumina.models import Session


def ping(request):
    if request.user.is_anonymous():
        username = ''
    else:
        username = request.user.username

    response_data = {
        'status': 'ok',
        'server_date_str': str(datetime.datetime.now()),
        'username': username,
        'sessionid': request.COOKIES.get('sessionid', ''),
        'csrftoken': request.COOKIES.get('csrftoken', ''),
    }

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def check_pending_uploads(request):
    if request.user.is_anonymous():
        response_data = {
            'status': 'ok',
            'username': '',
            'pending_uploads_count': 0,
            'pending_uploads': []
        }
    else:
        pending_sessions = Session.objects.get_pending_uploads(request.user)
        pending_session_list = []
        for pending_session in pending_sessions:
            pending_session_list.append({
                'id': pending_session.id,
                'name': pending_session.name,
            })
        response_data = {
            'status': 'ok',
            'username': request.user.username,
            'pending_uploads_count': len(pending_sessions),
            'pending_uploads': pending_session_list
        }

    return HttpResponse(json.dumps(response_data), content_type="application/json")
