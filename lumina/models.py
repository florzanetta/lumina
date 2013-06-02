from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


class ForUserManagerMixin():

    def for_user(self, user):
        """Filter objects by user"""
        return self.filter(user=user)


#===============================================================================
# Album
#===============================================================================

class AlbumManager(models.Manager, ForUserManagerMixin):
    pass


class Album(models.Model):
    name = models.CharField(max_length=300)
    user = models.ForeignKey(User)

    objects = AlbumManager()

    def __unicode__(self):
        return u"Album {0}".format(self.name)


#===============================================================================
# SharedAlbum
#===============================================================================

class SharedAlbumManager(models.Manager, ForUserManagerMixin):
    pass


class SharedAlbum(models.Model):
    shared_with = models.CharField(max_length=300)
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album, null=True)
    random_hash = models.CharField(max_length=36, unique=True) # len(uuid4) = 36

    objects = SharedAlbumManager()

    def __unicode__(self):
        return u"Shared Album {0}".format(self.album.name)


#===============================================================================
# Image
#===============================================================================

class ImageManager(models.Manager, ForUserManagerMixin):
    pass


class Image(models.Model):
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300)
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    # See: https://docs.djangoproject.com/en/1.5/topics/files/
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album, null=True)

    objects = ImageManager()

    def __unicode__(self):
        return u"Image {0}".format(self.image.url)

    def get_absolute_url(self):
        return reverse('image_update', kwargs={'pk': self.pk})
