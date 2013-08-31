# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, UserManager


class ForUserManagerMixin():

    def for_user(self, user):
        """Filter objects by user"""
        return self.filter(user=user)


class LuminaUserManager(UserManager):
    pass


class LuminaUser(AbstractUser):
    PHOTOGRAPHER = 'P'
    CUSTOMER = 'C'
    USER_TYPES = (
        (PHOTOGRAPHER, 'Fotografo'),
        (CUSTOMER, 'Cliente'),
    )
    user_type = models.CharField(max_length=1, choices=USER_TYPES, default=PHOTOGRAPHER)
    customer_of = models.ForeignKey('self', null=True, blank=True, related_name='customers')

    objects = LuminaUserManager()

    def all_my_customers(self):
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        # return self.filter(customer_of=self)
        return self.customers.all()

    def __unicode__(self):
        return u"{} ({})".format(self.get_full_name(), self.username)


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
        return self.filter(Q(user=user) | Q(shared_with=user)).distinct()


class Album(models.Model):
    name = models.CharField(max_length=300)
    user = models.ForeignKey(LuminaUser)  # owner
    shared_with = models.ManyToManyField(LuminaUser, blank=True,
                                         related_name='others_shared_albums')

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
    """
    Represents an album shared via email.

    An email is sent to the receiver, with a link to view the album.
    To view the almbum, the receiver just need the link, and doens't
    need to have an account nor bie logged in.

    Anyone with the link can see tha images of the album.

    With the current implementation, all the images of the album
    can be seen, and downloaded.
    """
    shared_with = models.EmailField(max_length=254)
    # https://docs.djangoproject.com/en/1.5/ref/models/fields/#emailfield
    user = models.ForeignKey(LuminaUser)
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


#===============================================================================
# ImageSelection
#===============================================================================

class ImageSelectionManager(models.Manager):

    def pending_image_selections(self, user):
        """
        Returns ImageSelection instances for which the customer
        has to do the selection of the images.
        """
        return self.filter(customer=user, status=ImageSelection.STATUS_WAITING)

    def all_my_accessible_imageselections(self, user):
        """
        Returns all the ImageSelection instances including those for what the user
        is the customer, and those for what the user is the owner of the album
        """
        return self.filter(Q(customer=user) | Q(album__user=user))

    def all_my_imageselections_as_customer(self, user, just_pending=False):
        """
        Returns a queryset filtering the ImageSelections for the specified user.
        If just_pending=True, returns only the ImageSelections waiting for the actual selection.
        """
        qs = self.filter(customer=user)
        if just_pending:
            qs = qs.filter(status=ImageSelection.STATUS_WAITING)
        return qs


class ImageSelection(models.Model):
    """
    Represents a request of the phtographer (user) to one
    of his customers (customer) to let the customer select
    which of the images of the album he wants.

    The customer will be able to see thumbnails of the images
    in low resolution, select the images he/she wants, and after
    confirming the selection, download the selected images in full-resolution.

    The `user` should be the owner of the `album`.
    """
    STATUS_WAITING = 'W'
    STATUS_IMAGES_SELECTED = 'S'
    STATUS = (
        (STATUS_WAITING, u'Esperando selección de cliente'),
        (STATUS_IMAGES_SELECTED, u'Seleccion realizada'),
    )
    user = models.ForeignKey(LuminaUser, related_name='+')
    album = models.ForeignKey(Album)
    customer = models.ForeignKey(LuminaUser, related_name='+')
    image_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STATUS, default=STATUS_WAITING)

    selected_images = models.ManyToManyField('Image', blank=True)

    objects = ImageSelectionManager()

    def clean(self):
        # from django.core.exceptions import ValidationError
        if self.id is None:
            image_count = self.album.image_set.count()
            if self.image_quantity > image_count:
                msg = {'image_quantity': 'Debe seleccionar {} o menos imagenes'.format(
                    image_count)}
                raise ValidationError(msg)


#===============================================================================
# Image
#===============================================================================

class ImageManager(models.Manager, ForUserManagerMixin):

    def all_my_images(self, user):
        """Returns all the user's images"""
        return self.for_user(user)

    def all_previsualisable(self, user):
        """
        Returns all the visible images for preview, ie: thumbnails or low quality.

        Some of the images may be downloaded (in full resolution).
        (ie: the user's images + the images of shared albums of other users)
        but other won't be downloadable (images from ImageSelection)
        """
        q = Q(user=user)
        q = q | Q(album__shared_with=user)
        q = q | Q(album__imageselection__customer=user)
        return self.filter(q).distinct()

    def get_for_download(self, user, image_id):
        """
        Returns an images to be downloaded by the user
        """
        # Original implementation (returns filtered result)
        # return self.filter(
        #    Q(user=user) |
        #    Q(album__shared_with=user)
        # )
        #
        # This ***might*** work, using F() queries:
        # return self.filter(
        #    Q(user=user) |
        #    Q(album__shared_with=user) |
        #    Q(imageselection__customer=user, imageselection__selected_images=F('id'))
        # )

        try:
            # The user owns the image?
            return self.get(user=user, id=image_id)
        except Image.DoesNotExist:
            pass

        try:
            # The image was shared with the user?
            return self.get(album__shared_with=user, id=image_id)
        except Image.DoesNotExist:
            pass

        # Tha image was selected by the user?
        return self.get(imageselection__customer=user, imageselection__selected_images=image_id)


class Image(models.Model):
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    # See: https://docs.djangoproject.com/en/1.5/topics/files/
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300)
    size = models.PositiveIntegerField()
    original_filename = models.CharField(max_length=128)
    content_type = models.CharField(max_length=64)
    user = models.ForeignKey(LuminaUser)
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
