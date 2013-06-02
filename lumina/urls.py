from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required

from lumina.views import ImageCreateView, ImageUpdateView, ImageListView,\
    AlbumListView, AlbumDetailView, AlbumCreateView, AlbumUpdateView

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

# TODO: See: http://django-braces.readthedocs.org/en/latest/index.html#loginrequiredmixin

urlpatterns = patterns('',
    url(r'^$', 'lumina.views.home', name='home'),

    #===========================================================================
    # Album
    #===========================================================================
    url(r'^album/list/$', login_required(AlbumListView.as_view()),
        name='album_list'),
    url(r'^album/detail/(?P<pk>\d+)/$', login_required(AlbumDetailView.as_view()),
        name='album_detail'),
    url(r'^album/create/$', login_required(AlbumCreateView.as_view()),
        name='album_create'),
    url(r'^album/update/(?P<pk>\d+)/$', login_required(AlbumUpdateView.as_view()),
        name='album_update'),

    #===========================================================================
    # Album
    #===========================================================================
    url(r'^shared/album/view/(?P<random_hash>[a-f0-9-]{36})/$',
        'lumina.views.shared_album_view', name='shared_album_view'),
    url(r'^shared/album/view/(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        'lumina.views.shared_album_image_thumb_64x64', name='shared_album_image_thumb_64x64'),
    url(r'^shared/album/download/(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        'lumina.views.shared_album_image_download', name='shared_album_image_download'),


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
