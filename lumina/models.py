from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied


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

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'pk': self.pk})


#===============================================================================
# SharedAlbum
#===============================================================================

class SharedAlbumManager(models.Manager, ForUserManagerMixin):
    pass


class SharedAlbum(models.Model):
    shared_with = models.EmailField(max_length=254)
    # https://docs.djangoproject.com/en/1.5/ref/models/fields/#emailfield
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album)
    random_hash = models.CharField(max_length=36, unique=True) # len(uuid4) = 36

    objects = SharedAlbumManager()

    def __unicode__(self):
        return u"Shared Album {0} with {1}".format(self.album.name, self.shared_with)

    def get_image_from_album(self, image_id):
        """
        Returns the image with 'id' = 'image_id' only
        if the image is part of the shared album.
        """
        image = Image.objects.get(pk=image_id)
        if self.album == image.album:
            return image
        else:
            raise(PermissionDenied("The Image {0} doesn't belong to the SharedAlbum {1}".format(
                image_id, self.id)))


#===============================================================================
# Image
#===============================================================================

class ImageManager(models.Manager, ForUserManagerMixin):
    pass


class Image(models.Model):
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    # See: https://docs.djangoproject.com/en/1.5/topics/files/
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300)
    size = models.PositiveIntegerField()
    original_filename = models.CharField(max_length=128)
    content_type = models.CharField(max_length=64)
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album, null=True)

    objects = ImageManager()

    def __unicode__(self):
        return u"Image {0}".format(self.original_filename)

    def get_absolute_url(self):
        return reverse('image_update', kwargs={'pk': self.pk})

    def set_content_type(self, content_type):
        """Set content_type, truncating if it's too large"""
        self.content_type = content_type[0:64]

    def set_original_filename(self, filename):
        """Set original filename, truncating if it's too large"""
        self.original_filename = filename[0:128]
