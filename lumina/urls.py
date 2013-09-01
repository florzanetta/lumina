from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from lumina.views import SessionListView, SessionDetailView, SessionCreateView,\
    SessionUpdateView, CustomerListView, CustomerCreateView, CustomerUpdateView,\
    UserListView, ImageListView


# Uncomment the next two lines to enable the admin:
admin.autodiscover()

# TODO: See: http://django-braces.readthedocs.org/en/latest/index.html#loginrequiredmixin

urlpatterns = patterns(
    '',

#     url(r'^test_html5_upload$', 'lumina.views.test_html5_upload', name='test_html5_upload'),
#     url(r'^test_html5_upload_ajax', 'lumina.views.test_html5_upload_ajax',
#         name='test_html5_upload_ajax'),

    #===========================================================================
    # Home
    #===========================================================================
    url(r'^$', 'lumina.views.home', name='home'),

    #===========================================================================
    # Album
    #===========================================================================
    url(r'^session/list/$',
        cache_control(private=True)(
            login_required(
                SessionListView.as_view())),
        name='session_list'),

    url(r'^session/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionDetailView.as_view())),
        name='session_detail'),

    url(r'^session/create/$',
        cache_control(private=True)(
            login_required(SessionCreateView.as_view())),
        name='session_create'),

    url(r'^session/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionUpdateView.as_view())),
        name='session_update'),

    #===========================================================================
    # SharedAlbum
    #===========================================================================
#     url(r'^shared/album/anonymous/view/(?P<random_hash>[a-f0-9-]{36})/$',
#         cache_control(private=True)(
#             SharedAlbumAnonymousView.as_view()),
#         name='shared_album_view'),
#
#     url(r'^shared/album/create/$',
#         cache_control(private=True)(
#             login_required(
#                 SharedAlbumCreateView.as_view())),
#         name='shared_album_create'),
#
#     url(r'^shared/album/anonymous/view/(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
#         'lumina.views.shared_album_image_thumb_64x64',
#         name='shared_album_image_thumb_64x64'),
#
#     url(r'^shared/album/anonymous/download/(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
#         'lumina.views.shared_album_image_download',
#         name='shared_album_image_download'),
#
#     url(r'^shared/album/selection/$',
#         cache_control(private=True)(
#             login_required(
#                 ImageSelectionCreateView.as_view())),
#         name='image_selection_create'),

    #===========================================================================
    # ImageSelection
    #===========================================================================
#     url(r'^imageselection/list/$',
#         cache_control(private=True)(
#             login_required(
#                 ImageSelectionListView.as_view())),
#         name='imageselection_list'),
#
#     url(r'^imageselection/redirect/(?P<pk>\d+)/$',
#         'lumina.views.imageselection_redirect',
#         name='imageselection_redirect'),
#
#     url(r'^imageselection/detail/(?P<pk>\d+)/$',
#         cache_control(private=True)(
#             login_required(ImageSelectionDetailView.as_view())),
#         name='imageselection_detail'),
#
#     url(r'^imageselection/select_images/(?P<pk>\d+)/$',
#         cache_control(private=True)(
#             login_required(ImageSelectionForCustomerView.as_view())),
#         name='imageselection_select_images'),

    #===========================================================================
    # Image
    #===========================================================================
    url(r'^image/list/$',
        cache_control(private=True)(
            login_required(ImageListView.as_view())),
        name='image_list'),
#
#     url(r'^image/create/$',
#         cache_control(private=True)(
#             login_required(ImageCreateView.as_view())),
#         name='image_create'),
#
#     url(r'^image/update/(?P<pk>\d+)/$',
#         cache_control(private=True)(
#             login_required(ImageUpdateView.as_view())),
#         name='image_update'),
#
#     url(r'^image/(\d+)/thumb/$', 'lumina.views.image_thumb',
#         name='image_thumb'),
#
#     url(r'^image/(\d+)/thumb/64x64/$', 'lumina.views.image_thumb_64x64',
#         name='image_thumb_64x64'),
#
#     url(r'^image/(\d+)/download/$',
#         'lumina.views.image_download',
#         name='image_download'),

    #===========================================================================
    # Customer
    #===========================================================================
    url(r'^customer/list/$',
        cache_control(private=True)(
            login_required(CustomerListView.as_view())),
        name='customer_list'),

    url(r'^customer/create/$',
        cache_control(private=True)(
            login_required(CustomerCreateView.as_view())),
        name='customer_create'),

    url(r'^customer/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(CustomerUpdateView.as_view())),
        name='customer_update'),

    #===========================================================================
    # Users
    #===========================================================================
    url(r'^customer/user/list/(?P<customer_id>\d+)/$',
        cache_control(private=True)(
            login_required(UserListView.as_view())),
        name='customer_user_list'),

#     url(r'^customer/user/create/$',
#         cache_control(private=True)(
#             login_required(UserCreateView.as_view())),
#         name='customer_user_create'),
#
#     url(r'^customer/user/update/(?P<pk>\d+)/$',
#         cache_control(private=True)(
#             login_required(UserUpdateView.as_view())),
#         name='customer_user_update'),

    #===========================================================================
    # Rest API
    #===========================================================================
#    url(r'^rest/', include('lumina.urls_rest')),

    #
    # Other
    #
    url(r'^admin/check/403$', 'lumina.views.check_403', name='check_403'),
    url(r'^admin/check/404$', 'lumina.views.check_404', name='check_404'),
    url(r'^admin/check/500$', 'lumina.views.check_500', name='check_500'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/', },
        name='logout',),

    #
    # django-social-auth
    #
    url(r'^social_auth/', include('social_auth.urls')),
)
