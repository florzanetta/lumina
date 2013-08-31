from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',

    url(r'^ping$', 'lumina.views_rest.ping', name='rest_ping'),
    url(r'^check_pending_uploads', 'lumina.views_rest.check_pending_uploads',
        name='check_pending_uploads'),

)
