from django.db import models
from django.contrib.auth.models import User


class ImageManager(models.Manager):
    
    def all_from_user(self, user):
        """Returns all the images for the user"""
        return self.filter(user=user)


class Image(models.Model):
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300)
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    user = models.ForeignKey(User)

    objects = ImageManager()

    def __unicode__(self):
        return u"Image {0}".format(self.image.url)
