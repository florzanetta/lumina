from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from lumina.views import ImageCreateView, ImageUpdateView, ImageListView,\
    AlbumListView, AlbumDetailView

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'lumina.views.home', name='home'),

    #===========================================================================
    # Album
    #===========================================================================
    url(r'^album/list/$', login_required(AlbumListView.as_view()),
        name='album_list'),
    url(r'^album/detail/(?P<pk>\d+)/$', login_required(AlbumDetailView.as_view()),
        name='album_detail'),

    #===========================================================================
    # Image
    #===========================================================================
    url(r'^image/list/$', login_required(ImageListView.as_view()),
        name='image_list'),
    url(r'^image/create/$', login_required(ImageCreateView.as_view()),
        name='image_create'),
    url(r'^image/update/(?P<pk>\d+)/$', login_required(ImageUpdateView.as_view()),
        name='image_update'),
    url(r'^image/(\d+)/thumb/$', 'lumina.views.image_thumb',
        name='image_thumb'),
    url(r'^image/(\d+)/thumb/64x64/$', 'lumina.views.image_thumb_64x64',
        name='image_thumb_64x64'),

    #
    # Other
    #
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
    }, name='logout',),
)
