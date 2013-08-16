from django.contrib import admin
from lumina.models import Image, Album, SharedAlbum, \
    ImageSelection, LuminaUser

admin.site.register(Image)
admin.site.register(Album)
admin.site.register(SharedAlbum)
admin.site.register(LuminaUser)
admin.site.register(ImageSelection)
