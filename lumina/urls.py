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
from lumina import views_customer
from lumina import views_customer_type
from lumina import views_session_type
from lumina import views_preview_size
from lumina import views_user_customer
from lumina import views_user_preferences
from lumina import views_user_studio
from lumina import views_session
from lumina import views_image
from lumina import views_shared_session
from lumina import views_session_quote
from lumina import views_studio

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
                views_session.SessionListView.as_view())),
        name='session_list'),

    url(r'^session/search/$',
        cache_control(private=True)(
            login_required(
                views_session.SessionSearchView.as_view())),
        name='session_search'),

    url(r'^session/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_session.SessionDetailView.as_view())),
        name='session_detail'),

    url(r'^session/(?P<pk>\d+)/set-image-as-album-icon/(?P<image_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_session.SetImageAsAlbumIconView.as_view())),
        name='set_image_as_album_icon'),

    url(r'^session/(?P<pk>\d+)/album-icon/$',
        cache_control(private=True)(
            login_required(views_session.AlbumIconView.as_view())),
        name='session_album_icon'),

    url(r'^session/create/$',
        cache_control(private=True)(
            login_required(views_session.SessionCreateView.as_view())),
        name='session_create'),

    url(r'^session/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_session.SessionUpdateView.as_view())),
        name='session_update'),

    url(r'^session/create-from-quote/(?P<session_quote_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_session.SessionCreateFromQuoteView.as_view())),
        name='session_create_from_quote'),

    # UPLOADS

    url(r'^session/upload-previews/(?P<pk>\d+)/$',
        cache_control(private=True)(login_required(views_session.SessionUploadPreviewsView.as_view())),
        name='session_upload_previews'),

    url(r'^session/upload-previews/(?P<session_id>\d+)/upload/',
        views_session.session_upload_previews_upload,
        name='session_upload_previews_upload'),


    # ===========================================================================
    # SharedSessionByEmail
    # ===========================================================================
    url(r'^session/shared-by-email/create/$',
        cache_control(private=True)(
            login_required(
                views_shared_session.SharedSessionByEmailCreateView.as_view())),
        name='shared_session_by_email_create'),

    url(r'^session/shared-by-email/anonymous/view/'
        '(?P<random_hash>[a-f0-9-]{36})/$',
        cache_control(private=True)(
            views_shared_session.SharedSessionByEmailAnonymousView.as_view()),
        name='shared_session_by_email_view'),

    url(r'^session/shared-by-email/anonymous/view/'
        '(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        views_shared_session.shared_session_by_email_image_thumb_64x64,
        name='shared_session_by_email_image_thumb_64x64'),

    url(r'^session/shared-by-email/anonymous/download/'
        '(?P<random_hash>[a-f0-9-]{36})/(?P<image_id>\d+)/$',
        views_shared_session.shared_session_by_email_image_download,
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

    url(r'^session/image-selection/awaiting-customer-selection/list/$',
        cache_control(private=True)(
            login_required(
                views_image_selection.ImageSelectionAwaitingCustomerSelectionListView.as_view())),
        name='imageselection_awaiting_customer_selection_list'),

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
            login_required(views_image.ImageListView.as_view())),
        name='image_list'),

    url(r'^image/create/$',
        cache_control(private=True)(
            login_required(views_image.ImageCreateView.as_view())),
        name='image_create'),

    url(r'^image/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_image.ImageUpdateView.as_view())),
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
    # Customer Types
    # ===========================================================================
    url(r'^customer-type/list/$',
        cache_control(private=True)(
            login_required(views_customer_type.CustomerTypeListView.as_view())),
        name='customer_type_list'),

    url(r'^customer-type/create/$',
        cache_control(private=True)(
            login_required(views_customer_type.CustomerTypeCreateView.as_view())),
        name='customer_type_create'),

    url(r'^customer-type/(?P<customer_type_id>\d+)/update/$',
        cache_control(private=True)(
            login_required(views_customer_type.CustomerTypeUpdateView.as_view())),
        name='customer_type_update'),

    url(r'^customer-type/(?P<customer_type_id>\d+)/archive/$',
        cache_control(private=True)(
            login_required(views_customer_type.CustomerTypeArchiveView.as_view(archive=True))),
        name='customer_type_archive'),

    url(r'^customer-type/(?P<customer_type_id>\d+)/unarchive/$',
        cache_control(private=True)(
            login_required(views_customer_type.CustomerTypeArchiveView.as_view(archive=False))),
        name='customer_type_unarchive'),

    # ===========================================================================
    # Customer
    # ===========================================================================

    url(r'^customer/list/$',
        cache_control(private=True)(
            login_required(views_customer.CustomerListView.as_view())),
        name='customer_list'),

    url(r'^customer/create/$',
        cache_control(private=True)(
            login_required(views_customer.CustomerCreateView.as_view())),
        name='customer_create'),

    url(r'^customer/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_customer.CustomerUpdateView.as_view())),
        name='customer_update'),

    # ===========================================================================
    # Customer's Users
    # ===========================================================================

    url(r'^customer/user/list/(?P<customer_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_user_customer.CustomerUserListView.as_view())),
        name='customer_user_list'),

    url(r'^customer/user/create/(?P<customer_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_user_customer.CustomerUserCreateView.as_view())),
        name='customer_user_create'),

    url(r'^customer/user/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_user_customer.CustomerUserUpdateView.as_view())),
        name='customer_user_update'),

    # ===========================================================================
    # Studio's Users
    # ===========================================================================

    url(r'^studio/user/list/$',
        cache_control(private=True)(
            login_required(views_user_studio.StudioUserListView.as_view())),
        name='studio_user_list'),

    url(r'^studio/user/create/$',
        cache_control(private=True)(
            login_required(views_user_studio.StudioUserCreateView.as_view())),
        name='studio_user_create'),

    url(r'^studio/user/update/(?P<photographer_user_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_user_studio.StudioUserUpdateView.as_view())),
        name='studio_user_update'),

    # ===========================================================================
    # Session Types
    # ===========================================================================

    url(r'^session-type/list/$',
        cache_control(private=True)(
            login_required(views_session_type.SessionTypeListView.as_view())),
        name='session_type_list'),

    url(r'^session-type/create/$',
        cache_control(private=True)(
            login_required(views_session_type.SessionTypeCreateView.as_view())),
        name='session_type_create'),

    url(r'^session-type/(?P<session_type_id>\d+)/update/$',
        cache_control(private=True)(
            login_required(views_session_type.SessionTypeUpdateView.as_view())),
        name='session_type_update'),

    url(r'^session-type/(?P<session_type_id>\d+)/archive/$',
        cache_control(private=True)(
            login_required(views_session_type.SessionTypeArchiveView.as_view(archive=True))),
        name='session_type_archive'),

    url(r'^session-type/(?P<session_type_id>\d+)/unarchive/$',
        cache_control(private=True)(
            login_required(views_session_type.SessionTypeArchiveView.as_view(archive=False))),
        name='session_type_unarchive'),


    # ===========================================================================
    # Preview Size
    # ===========================================================================

    url(r'^preview-size/list/$',
        cache_control(private=True)(
            login_required(views_preview_size.PreviewSizeListView.as_view())),
        name='preview_size_list'),

    url(r'^preview-size/create/$',
        cache_control(private=True)(
            login_required(views_preview_size.PreviewSizeCreateView.as_view())),
        name='preview_size_create'),

    url(r'^preview-size/(?P<preview_size_id>\d+)/update/$',
        cache_control(private=True)(
            login_required(views_preview_size.PreviewSizeUpdateView.as_view())),
        name='preview_size_update'),

    url(r'^preview-size/(?P<preview_size_id>\d+)/archive/$',
        cache_control(private=True)(
            login_required(views_preview_size.PreviewSizeArchiveView.as_view(archive=True))),
        name='preview_size_archive'),

    url(r'^preview-size/(?P<preview_size_id>\d+)/unarchive/$',
        cache_control(private=True)(
            login_required(views_preview_size.PreviewSizeArchiveView.as_view(archive=False))),
        name='preview_size_unarchive'),

    # ===========================================================================
    # User Preferences
    # ===========================================================================

    url(r'^user/preferences/$',
        cache_control(private=True)(
            login_required(views_user_preferences.UserPreferenceUpdateView.as_view())),
        name='user_preferences_update'),

    # ===========================================================================
    # SessionQuote
    # ===========================================================================

    url(r'^quote/create/$',
        cache_control(private=True)(
            login_required(views_session_quote.SessionQuoteCreateView.as_view())),
        name='quote_create'),

    url(r'^quote/list/$',
        cache_control(private=True)(
            login_required(
                views_session_quote.SessionQuoteListView.as_view())),
        name='quote_list'),

    url(r'^quote/list/pending_for_cusomter/$',
        cache_control(private=True)(
            login_required(
                views_session_quote.SessionQuotePendigForCustomerListView.as_view())),
        name='quote_list_pending_for_customer'),

    url(r'^quote/search/$',
        cache_control(private=True)(
            login_required(
                views_session_quote.SessionQuoteSearchView.as_view())),
        name='quote_search'),

    url(r'^quote/detail/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_session_quote.SessionQuoteDetailView.as_view())),
        name='quote_detail'),

    url(r'^quote/update/(?P<pk>\d+)/$',
        cache_control(private=True)(
            login_required(views_session_quote.SessionQuoteUpdateView.as_view())),
        name='quote_update'),


    # ===========================================================================
    # SessionQuote
    # ===========================================================================

    url(r'^quote/alternatives/choose/(?P<pk>\d+)/$',  # for customer
        cache_control(private=True)(
            login_required(views_session_quote.SessionQuoteAlternativeSelectView.as_view())),
        name='quote_choose_alternative'),

    url(r'^quote/alternatives/create/(?P<session_quote_id>\d+)/$',
        cache_control(private=True)(
            login_required(views_session_quote.SessionQuoteAlternativeCreateView.as_view())),
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
    # Studio
    # ===========================================================================

    url(r'^studio/update/$',
        cache_control(private=True)(
            login_required(
                views_studio.StudioUpdateView.as_view())),
        name='studio_update'),

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
