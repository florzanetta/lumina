from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

import autocomplete_light

from lumina.views import SessionListView, SessionDetailView, SessionCreateView, \
    SessionUpdateView, CustomerListView, CustomerCreateView, CustomerUpdateView, \
    UserListView, ImageListView, UserCreateView, UserUpdateView, \
    SharedSessionByEmailCreateView, SharedSessionByEmailAnonymousView, \
    ImageCreateView, ImageUpdateView, ImageSelectionCreateView, \
    ImageSelectionListView, ImageSelectionDetailView, \
    ImageSelectionForCustomerView, SessionUploadPreviewsView,\
    SessionQuoteCreateView, SessionQuoteListView, SessionQuoteDetailView,\
    SessionQuoteUpdateView, \
    SessionQuoteAlternativeSelectView, SessionQuoteAlternativeCreateView

autocomplete_light.autodiscover()  # BEFORE admin.autodiscover()
admin.autodiscover()

# TODO: See: http://django-braces.readthedocs.org/en/latest/index.html#loginrequiredmixin

urlpatterns = patterns(
    '',

    #===========================================================================
    # Home
    #===========================================================================
    url(r'^$', 'lumina.views.home', name='home'),

    #===========================================================================
    # Session
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

    url(r'^session/upload-previews/(?P<pk>\d+)/$',
        cache_control(private=True)(login_required(SessionUploadPreviewsView.as_view())),
        name='session_upload_previews'),

    url(r'^session/upload-previews/(?P<session_id>\d+)/upload/',
        'lumina.views.session_upload_previews_upload',
        name='session_upload_previews_upload'),


    #===========================================================================
    # SharedSessionByEmail
    #===========================================================================
    url(r'^session/shared-by-email/create/$',
        cache_control(private=True)(
            login_required(
                SharedSessionByEmailCreateView.as_view())),
        name='shared_session_by_email_create'),

    url(r'^session/shared-by-email/anonymous/view/'
        '(?P<random_hash>[a-f0-9-]{36})/$',
        cache_control(private=True)(
            SharedSessionByEmailAnonymousView.as_view()),
        name='shared_session_by_email_view'),

    url(r'^session/shared-by-email/anonymous/view/'
        '(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        'lumina.views.shared_session_by_email_image_thumb_64x64',
        name='shared_session_by_email_image_thumb_64x64'),

    url(r'^session/shared-by-email/anonymous/download/'
        '(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        'lumina.views.shared_session_by_email_image_download',
        name='shared_session_by_email_image_download'),

    #===========================================================================
    # ImageSelection
    #===========================================================================
    url(r'^session/image-selection/create/$',
        cache_control(private=True)(
            login_required(
                ImageSelectionCreateView.as_view())),
        name='image_selection_create'),

    url(r'^session/image-selection/list/$',
        cache_control(private=True)(
            login_required(
                ImageSelectionListView.as_view())),
        name='imageselection_list'),

    url(r'^session/image-selection/redirect/(?P<pk>\d+)/$',
        'lumina.views.imageselection_redirect',
        name='imageselection_redirect'),

    url(r'^session/image-selection/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(ImageSelectionDetailView.as_view())),
        name='imageselection_detail'),

    url(r'^session/image-selection/select_images/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(ImageSelectionForCustomerView.as_view())),
        name='imageselection_select_images'),

    #===========================================================================
    # Image
    #===========================================================================
    url(r'^image/list/$',
        cache_control(private=True)(
            login_required(ImageListView.as_view())),
        name='image_list'),

    url(r'^image/create/$',
        cache_control(private=True)(
            login_required(ImageCreateView.as_view())),
        name='image_create'),

    url(r'^image/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(ImageUpdateView.as_view())),
        name='image_update'),

    url(r'^image/(\d+)/thumb/$', 'lumina.views.image_thumb',
        name='image_thumb'),

    url(r'^image/(\d+)/thumb/64x64/$', 'lumina.views.image_thumb_64x64',
        name='image_thumb_64x64'),

    url(r'^image/(\d+)/download/$',
        'lumina.views.image_download',
        name='image_download'),

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

    url(r'^customer/user/create/(?P<customer_id>\d+)/$',
        cache_control(private=True)(
            login_required(UserCreateView.as_view())),
        name='customer_user_create'),

    url(r'^customer/user/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(UserUpdateView.as_view())),
        name='customer_user_update'),


    #===========================================================================
    # SessionQuote
    #===========================================================================

    url(r'^quote/create/$',
        cache_control(private=True)(
            login_required(SessionQuoteCreateView.as_view())),
        name='quote_create'),

    url(r'^quote/list/$',
        cache_control(private=True)(
            login_required(
                SessionQuoteListView.as_view())),
        name='quote_list'),

    url(r'^quote/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteDetailView.as_view())),
        name='quote_detail'),

    url(r'^quote/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteUpdateView.as_view())),
        name='quote_update'),


    #===========================================================================
    # SessionQuote
    #===========================================================================

    url(r'^quote/alternatives/choose/(?P<pk>\d+)/$',  # for customer
        cache_control(private=True)(
            login_required(SessionQuoteAlternativeSelectView.as_view())),
        name='quote_choose_alternative'),

    url(r'^quote/alternatives/create/(?P<session_quote_id>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteAlternativeCreateView.as_view())),
        name='quote_alternatives_create'),



    #===========================================================================
    # Rest API
    #===========================================================================

    url(r'^rest/', include('lumina.urls_rest')),

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

    #
    # autocomplete_light
    #
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)
