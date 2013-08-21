from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',

    url(r'^ping$', 'lumina.views_rest.ping', name='rest_ping'),

)
