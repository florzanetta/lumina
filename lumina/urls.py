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
    url(r'^image/add/$', login_required(ImageCreateView.as_view()),
        name='image_add'),
    url(r'^image/edit/(?P<pk>\d+)/$', login_required(ImageUpdateView.as_view()),
        name='image_edit'),
    url(r'^image/(\d+)/thumb/$', 'lumina.views.image_thumb',
        name='image_thumb'),

    #
    # Other
    #
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout', {
        'next_page': '/',
    }, name='logout',),
)
