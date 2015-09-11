import autocomplete_light

from django.contrib import admin
from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control

from lumina import views
from lumina import views_image_selection_creation
from lumina import views_image_selection_upload
from lumina import views_image_selection
from lumina import views_reports

from lumina.views_user import (
    UserListView,  UserCreateView, UserUpdateView,
    UserPreferenceUpdateView
)

from lumina.views_customer import *
from lumina.views_image import *
from lumina.views_shared_session import *
from lumina.views_session import *
from lumina.views_session_quote import *

autocomplete_light.autodiscover()  # BEFORE admin.autodiscover()
admin.autodiscover()

# TODO: See: http://django-braces.readthedocs.org/en/latest/index.html#loginrequiredmixin

urlpatterns = patterns(
    '',

    # ===========================================================================
    # Home
    # ===========================================================================
    url(r'^$', views.home, name='home'),

    # ===========================================================================
    # Session
    # ===========================================================================
    url(r'^session/list/$',
        cache_control(private=True)(
            login_required(
                SessionListView.as_view())),
        name='session_list'),

    url(r'^session/search/$',
        cache_control(private=True)(
            login_required(
                SessionSearchView.as_view())),
        name='session_search'),

    url(r'^session/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionDetailView.as_view())),
        name='session_detail'),

    url(r'^session/(?P<pk>\d+)/set-image-as-album-icon/(?P<image_id>\d+)/$',
        cache_control(private=True)(
            login_required(SetImageAsAlbumIconView.as_view())),
        name='set_image_as_album_icon'),

    url(r'^session/(?P<pk>\d+)/album-icon/$',
        cache_control(private=True)(
            login_required(AlbumIconView.as_view())),
        name='session_album_icon'),

    url(r'^session/create/$',
        cache_control(private=True)(
            login_required(SessionCreateView.as_view())),
        name='session_create'),

    url(r'^session/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionUpdateView.as_view())),
        name='session_update'),

    # UPLOADS

    url(r'^session/upload-previews/(?P<pk>\d+)/$',
        cache_control(private=True)(login_required(SessionUploadPreviewsView.as_view())),
        name='session_upload_previews'),

    url(r'^session/upload-previews/(?P<session_id>\d+)/upload/',
        session_upload_previews_upload,
        name='session_upload_previews_upload'),


    # ===========================================================================
    # SharedSessionByEmail
    # ===========================================================================
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
        shared_session_by_email_image_thumb_64x64,
        name='shared_session_by_email_image_thumb_64x64'),

    url(r'^session/shared-by-email/anonymous/download/'
        '(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        shared_session_by_email_image_download,
        name='shared_session_by_email_image_download'),

    # ===========================================================================
    # ImageSelection
    # ===========================================================================
    url(r'^session/image-selection/create/$',
        cache_control(private=True)(
            login_required(
                views_image_selection_creation.ImageSelectionCreateView.as_view())),
        name='image_selection_create'),

    url(
        r'^session/image-selection/create/(?P<pk>\d+)/$',
        views_image_selection_creation.image_selection_create_from_quote,
        name='image_selection_create_from_quote'),

    url(r'^session/image-selection/list/$',
        cache_control(private=True)(
            login_required(
                views_image_selection.ImageSelectionListView.as_view())),
        name='imageselection_list'),

    url(r'^session/image-selection/with-pending-uploads/list/$',
        cache_control(private=True)(
            login_required(
                views_image_selection.ImageSelectionWithPendingUploadsListView.as_view())),
        name='imageselection_with_pending_uploads_list'),

    url(r'^session/image-selection/upload-pending/(?P<pk>\d+)/manual-upload/$',
        cache_control(private=True)(
            login_required(views_image_selection_upload.UploadPendingManualView.as_view())),
        name='imageselection_upload_pending_manual'),

    url(r'^session/image-selection/upload-pending/(?P<pk>\d+)/automatic-upload/$',
        cache_control(private=True)(
            login_required(views_image_selection_upload.UploadPendingAutomaticView.as_view())),
        name='imageselection_upload_pending_automatic'),

    url(r'^session/image-selection/upload-pending/(?P<pk>\d+)/all-images-already-uploaded/$',
        cache_control(private=True)(
            login_required(views_image_selection_upload.UploadPendingAllImagesAlreadyUploadedView.as_view())),
        name='imageselection_upload_pending_all_images_aready_uploaded'),

    url(r'^session/image-selection/redirect/(?P<pk>\d+)/$',
        views_image_selection.imageselection_redirect,
        name='imageselection_redirect'),

    url(r'^session/image-selection/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_image_selection.ImageSelectionDetailView.as_view())),
        name='imageselection_detail'),

    url(r'^session/image-selection/select_images/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_image_selection.ImageSelectionForCustomerView.as_view())),
        name='imageselection_select_images'),

    # ===========================================================================
    # Image
    # ===========================================================================
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

    url(r'^image/(\d+)/thumb/$',
        views.image_thumb,
        name='image_thumb'),

    url(r'^image/(\d+)/thumb/64x64/$',
        views.image_thumb_64x64,
        name='image_thumb_64x64'),

    url(r'^image/(\d+)/download/$',
        views.image_download,
        name='image_download'),

    url(r'^image/image_selection/(\d+)/download_all/$',
        views_image_selection.image_selection_download_selected_as_zip,
        name='image_selection_download_selected_as_zip'),

    url(r'^image/image_selection/(?P<image_selection_id>\d+)/thumbnail/(?P<image_id>\d+)/$',
        views_image_selection.image_selection_thumbnail,
        name='image_selection_thumbnail'),

    # ===========================================================================
    # Customer
    # ===========================================================================
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

    # ===========================================================================
    # Users
    # ===========================================================================
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

    url(r'^user/preferences/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(UserPreferenceUpdateView.as_view())),
        name='customer_user_preferences_update'),

    # ===========================================================================
    # SessionQuote
    # ===========================================================================

    url(r'^quote/create/$',
        cache_control(private=True)(
            login_required(SessionQuoteCreateView.as_view())),
        name='quote_create'),

    url(r'^quote/list/$',
        cache_control(private=True)(
            login_required(
                SessionQuoteListView.as_view())),
        name='quote_list'),

    url(r'^quote/list/pending_for_cusomter/$',
        cache_control(private=True)(
            login_required(
                SessionQuotePendigForCustomerListView.as_view())),
        name='quote_list_pending_for_customer'),

    url(r'^quote/search/$',
        cache_control(private=True)(
            login_required(
                SessionQuoteSearchView.as_view())),
        name='quote_search'),

    url(r'^quote/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteDetailView.as_view())),
        name='quote_detail'),

    url(r'^quote/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteUpdateView.as_view())),
        name='quote_update'),


    # ===========================================================================
    # SessionQuote
    # ===========================================================================

    url(r'^quote/alternatives/choose/(?P<pk>\d+)/$',  # for customer
        cache_control(private=True)(
            login_required(SessionQuoteAlternativeSelectView.as_view())),
        name='quote_choose_alternative'),

    url(r'^quote/alternatives/create/(?P<session_quote_id>\d+)/$',
        cache_control(private=True)(
            login_required(SessionQuoteAlternativeCreateView.as_view())),
        name='quote_alternatives_create'),


    # ===========================================================================
    # Reports
    # ===========================================================================

    url(r'^report/cost_vs_charged_by_customer_type/$',
        views_reports.view_report_cost_vs_charged_by_customer_type,
        name='report_cost_vs_charged_by_customer_type'),

    url(r'^report/extended_quotes_through_time/$',
        views_reports.view_extended_quotes_through_time,
        name='report_extended_quotes_through_time'),

    url(r'^report/extended_quotes_by_customer/$',
        views_reports.view_extended_quotes_by_customer,
        name='report_extended_quotes_by_customer'),

    url(r'^report/income_by_customer_type/$',
        views_reports.view_income_by_customer_type,
        name='report_income_by_customer_type'),


    # ===========================================================================
    # Studio preferences
    # ===========================================================================

    # FIXME: implement this view
    url(r'^studio/preview_sizes/$', 'lumina.views.home', name='studio_preview_sizes'),

    #
    # Other
    #
    url(r'^admin/check/403$', 'lumina.views_utils.check_403', name='check_403'),
    url(r'^admin/check/404$', 'lumina.views_utils.check_404', name='check_404'),
    url(r'^admin/check/500$', 'lumina.views_utils.check_500', name='check_500'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'lumina.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout',
        {'next_page': '/', },
        name='logout',),

    #
    # autocomplete_light
    #
    url(r'^autocomplete/', include('autocomplete_light.urls')),
)
