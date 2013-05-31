from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse


#===============================================================================
# Album
#===============================================================================

class AlbumManager(models.Manager):

    def for_user(self, user):
        """Returns all the albums for the user"""
        return self.filter(user=user)


class Album(models.Model):
    name = models.CharField(max_length=300)
    user = models.ForeignKey(User)

    objects = AlbumManager()

    def __unicode__(self):
        return u"Album {0}".format(self.name)


#===============================================================================
# Image
#===============================================================================

class ImageManager(models.Manager):
    
    def for_user(self, user):
        """Returns all the images for the user"""
        return self.filter(user=user)


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
        return reverse('image_detail', kwargs={'pk': self.pk})
