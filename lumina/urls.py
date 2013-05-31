from django.contrib import admin
from django.conf.urls import patterns, include, url

from lumina.views import ImageCreateView, ImageUpdateView
from django.contrib.auth.decorators import login_required

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    #
    # Lumina
    #
    url(r'^$', 'lumina.views.home', name='home'),
    url(r'^image/list/$', 'lumina.views.images_list', name='image_list'),
    url(r'^image/add/$', login_required(ImageCreateView.as_view()),
        name='image_add'),
    url(r'^image/view/(?P<pk>\d+)/$', login_required(ImageUpdateView.as_view()),
        name='image_detail'),

    #
    # Other
    #
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
    }, name='logout',),
)
