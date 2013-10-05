from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html

from lumina.models import LuminaUser, Image, Session, SharedSessionByEmail, \
    ImageSelection, Studio, Customer, SessionQuoteAlternative, SessionQuote,\
    UserPreferences, CustomerType, SessionType


class SharedSessionByEmailAdmin(admin.ModelAdmin):
    # https://docs.djangoproject.com/en/1.5/ref/contrib/admin/
    fields = ('generate_link', 'studio', 'session', 'shared_with', 'random_hash',)
    list_display = ('generate_link', 'studio', 'session', 'shared_with', 'random_hash')
    list_display_links = ('random_hash',)
    readonly_fields = ('generate_link',)

    def generate_link(self, instance):
        link = reverse('shared_session_by_email_view', args=[instance.random_hash])
        return format_html("<a href='{}' target='_blank'>Link</a>".format(link))

    generate_link.short_description = "Link"
    generate_link.allow_tags = True


admin.site.register(Customer)
admin.site.register(Image)
admin.site.register(ImageSelection)
admin.site.register(LuminaUser)
admin.site.register(Session)
admin.site.register(SessionQuote)
admin.site.register(SessionQuoteAlternative)
admin.site.register(SharedSessionByEmail, SharedSessionByEmailAdmin)
admin.site.register(Studio)
admin.site.register(UserPreferences)
admin.site.register(CustomerType)
admin.site.register(SessionType)
