from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.db.models import Q


class ForUserManagerMixin():

    def for_user(self, user):
        """Filter objects by user"""
        return self.filter(user=user)


#===============================================================================
# UserProxy
#===============================================================================

# https://docs.djangoproject.com/en/1.5/topics/db/models/#proxy-models

class UserProxyManager(models.Manager):

    def all_my_customers(self, user):
        return self.filter(luminauserprofile__customer_of=user)


class UserProxyExtraManagers(models.Model):
    custom_objects = UserProxyManager()

    class Meta:
        abstract = True


class UserProxy(User, UserProxyExtraManagers):

    class Meta:
        proxy = True


#===============================================================================
# Album
#===============================================================================

class AlbumManager(models.Manager, ForUserManagerMixin):

    def all_my_albums(self, user):
        """Returns all the user's albums"""
        return self.for_user(user)

    def shared_with_me(self, user):
        """Returns all the albums that other users have shared with 'user'"""
        return self.filter(shared_with=user)

    def all_visible(self, user):
        """
        Returns all the visible albums for an user
        (ie: the user's albums + the shared albums of other users)
        """
        return self.filter(Q(user=user) | Q(shared_with=user))


class Album(models.Model):
    name = models.CharField(max_length=300)
    user = models.ForeignKey(User)  # owner
    shared_with = models.ManyToManyField(User, blank=True, related_name='others_shared_albums')

    objects = AlbumManager()

    def __unicode__(self):
        return u"Album {0}".format(self.name)

    def get_absolute_url(self):
        return reverse('album_detail', kwargs={'pk': self.pk})


#===============================================================================
# SharedAlbum
#===============================================================================

class SharedAlbumManager(models.Manager, ForUserManagerMixin):

    def all_my_shares(self, user):
        """Returns all the shares"""
        return self.for_user(user)


class SharedAlbum(models.Model):
    shared_with = models.EmailField(max_length=254)
    # https://docs.djangoproject.com/en/1.5/ref/models/fields/#emailfield
    user = models.ForeignKey(User)
    album = models.ForeignKey(Album, related_name='shares_via_email')
    random_hash = models.CharField(max_length=36, unique=True)  # len(uuid4) = 36

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


class ImageSelection(models.Model):
    album = models.ForeignKey(Album)
    customer = models.ForeignKey(User)
    image_quantity = models.PositiveIntegerField()


#===============================================================================
# Image
#===============================================================================

class ImageManager(models.Manager, ForUserManagerMixin):

    def all_my_images(self, user):
        """Returns all the user's images"""
        return self.for_user(user)

    def all_visible(self, user):
        """
        Returns all the visible images for an user
        (ie: the user's images + the images of shared albums of other users)
        """
        return self.filter(Q(user=user) | Q(album__shared_with=user))


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


#===============================================================================
# LuminaUserProfile
#===============================================================================

class LuminaUserProfileManager(models.Manager):

    def for_user(self, user):
        """Filter objects by user"""
        return self.filter(customer_of=user)


class LuminaUserProfile(models.Model):
    # https://docs.djangoproject.com/en/1.5/topics/auth/customizing/\
    #    #extending-the-existing-user-model
    PHOTOGRAPHER = 'P'
    GUEST = 'G'
    USER_TYPES = (
        (PHOTOGRAPHER, 'Fotografo'),
        (GUEST, 'Invitado'),
    )
    user = models.OneToOneField(User)
    user_type = models.CharField(max_length=1, choices=USER_TYPES, default=PHOTOGRAPHER)
    customer_of = models.ForeignKey(User, related_name='customers')

    objects = LuminaUserProfileManager()

    def __unicode__(self):
        return u"Profile of '{0}'".format(self.user)
