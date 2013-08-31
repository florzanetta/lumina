from django.contrib import admin

from lumina.models import LuminaUser, Image, Session, SharedSessionByEmail, \
    ImageSelection, Studio, Customer

admin.site.register(Customer)
admin.site.register(Image)
admin.site.register(ImageSelection)
admin.site.register(LuminaUser)
admin.site.register(Session)
admin.site.register(SharedSessionByEmail)
admin.site.register(Studio)
