from django.contrib import admin
from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    #
    # Lumina
    #
    url(r'^$', 'lumina.views.home', name='home'),

    #
    # Other
    #
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'django.contrib.auth.views.login'),
)
