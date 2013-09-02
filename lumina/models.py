# -*- coding: utf-8 -*-

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Q
from django.contrib.auth.models import AbstractUser, UserManager


class ForUserManagerMixin():

    # FIXME: REFACTOR: refactor this (if needed)
    def for_user(self, user):
        """Filter objects by user"""
        return self.filter(user=user)


class LuminaUserManager(UserManager):
    """
    Manager for the LuminaUser model
    """
    pass


class LuminaUser(AbstractUser):
    """
    Represents a user who can log in and use the app.
    """
    PHOTOGRAPHER = 'P'
    CUSTOMER = 'C'
    USER_TYPES = (
        (PHOTOGRAPHER, 'Fotografo'),
        (CUSTOMER, 'Cliente'),
    )
    user_type = models.CharField(max_length=1, choices=USER_TYPES, default=PHOTOGRAPHER)

    # ----------------------------------------------------------------------
    # ----- Attributes for PHOTOGRAPHERS & CUSTOMERS
    # ----------------------------------------------------------------------

    # FIXME: REFACTOR: add common attributes, like phone, cellphone, address, etc.

    # ----------------------------------------------------------------------
    # ----- Attributes for PHOTOGRAPHERS // null=True, blank=True
    # ----------------------------------------------------------------------

    """
    Studio from which the photographer is part

    This should be None (NULL) for `user_type == CUSTOMER`.
    """
    studio = models.ForeignKey('Studio', related_name='photographers', null=True, blank=True)

    # ----------------------------------------------------------------------
    # ----- Attributes for CUSTOMERS // null=True, blank=True
    # ----------------------------------------------------------------------

    """
    user_for_customer: if not null, indicates that this instance (`self`) is
    a Django user associated to the `Customer` where `user_for_customer` points to.

    So, if `self.user_for_customer` points to "Customer XYZ", this means that the
    user referenced by `self` is a user for the customer "Customer XYZ".

    This should be None (NULL) for `user_type == PHOTOGRAPHER`.
    """
    # REFACTOR: used to be an attribute `customer_of` and point to `LuminaUser`
    # REFACTOR: `user_for_customer` is a new attribute
    user_for_customer = models.ForeignKey('Customer', null=True, blank=True, related_name='users')

    objects = LuminaUserManager()

    def is_photographer(self):
        return self.user_type == LuminaUser.PHOTOGRAPHER

    def is_for_customer(self):
        return self.user_type == LuminaUser.CUSTOMER

    def all_my_customers(self):
        """Returns queryset of Customer"""
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return Customer.objects.customers_of(self)

    def get_users_of_customer(self, customer_id):
        """
        Returns the users from the Customer with id = customer_id
        """
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return LuminaUser.objects.filter(user_type=LuminaUser.CUSTOMER,
                                   user_for_customer=customer_id,
                                   user_for_customer__studio=self.studio)

    def get_all_users(self):
        """
        Returns all the users of a Studio. This'll return all the user of all the customers
        """
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return LuminaUser.objects.filter(user_type=LuminaUser.CUSTOMER,
                                   user_for_customer__studio=self.studio)

    def __unicode__(self):
        return u"{} ({})".format(self.get_full_name(), self.username)


#===============================================================================
# Studio
#===============================================================================

class StudioManager(models.Manager):
    """
    Manager for the Studio model
    """
    pass


class Studio(models.Model):
    """
    Represents a photography studio. That is the organization
    that has many photographers.

    A `studio` instance has photo `session` (made by a `photographer`
    of the same `studio` for a specific `customer`).

    A `studio` instance has many `customers`. Customers are organizations
    who pays to the `studio`.
    """
    name = models.CharField(max_length=100)

    objects = StudioManager()

    def __unicode__(self):
        return u"Studio {0}".format(self.name)


#===============================================================================
# Customer
#===============================================================================

class CustomerManager(models.Manager):
    """
    Manager for the Customer model
    """

    def customers_of(self, photographer):
        """
        Returns the customers of the photographer's studio
        """
        return self.filter(studio=photographer.studio)


class Customer(models.Model):
    """
    A Customer (as the organization that pay to the photographer).

    A customer has many 'users'... all of them are employee of the Customer,
    or any person that the customer allowed to access the images.
    """
    name = models.CharField(max_length=100)
    studio = models.ForeignKey(Studio, related_name='customers')
    address = models.TextField()
    phone = models.CharField(max_length=20)

    objects = CustomerManager()

    def __unicode__(self):
        return u"Customer {0}".format(self.name)


#===============================================================================
# Session
#===============================================================================

class SessionManager(models.Manager, ForUserManagerMixin):
    """
    Manager for the Session model
    """

    def visible_sessions(self, user):
        """
        Returns the sessions the user can see (this means, this method
        may return sessions the user can see but not modify)
        """
        # FIXME: REFACTOR: add support for shared sessions
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            return self.filter(customer=user.user_for_customer)
        else:
            raise(Exception("User isn't PHOTOG. neither CUSTOMER - user: {}".format(user.id)))

    # FIXME: REFACTOR: refactor this (if needed)
    def all_my_albums(self, user):
        """Returns all the user's albums"""
        return self.for_user(user)

    # FIXME: REFACTOR: refactor this (if needed)
    def shared_with_me(self, user):
        """Returns all the albums that other users have shared with 'user'"""
        return self.filter(shared_with=user)

    # FIXME: REFACTOR: refactor this (if needed)
    def all_visible(self, user):
        """
        Returns all the visible albums for an user
        (ie: the user's albums + the shared albums of other users)
        """
        return self.filter(Q(user=user) | Q(shared_with=user)).distinct()


# FIXME: REFACTOR: change uses of `Album` to `Session` in views, etc.
class Session(models.Model):
    """
    Represents a photo session.
    """
    name = models.CharField(max_length=300)

    # REFACTOR: `studio` used to be named `user` and point to `LuminaUser`
    studio = models.ForeignKey(Studio)

    photographer = models.ForeignKey(LuminaUser)

    # REFACTOR: `customer` is a new attribute
    customer = models.ForeignKey(Customer)

    # REFACTOR: `shared_with` used to point to `LuminaUser`
    shared_with = models.ManyToManyField(Customer, blank=True,
                                         related_name='sessions_shared_with_me')

    objects = SessionManager()

    def __unicode__(self):
        return u"Session {0}".format(self.name)

    # FIXME: REFACTOR: refactor this (if needed)
    def get_absolute_url(self):
        return reverse('session_detail', kwargs={'pk': self.pk})


#===============================================================================
# SharedSessionByEmail (ex: SharedAlbum)
#===============================================================================

class SharedSessionByEmailManager(models.Manager, ForUserManagerMixin):
    """
    Manager for the SharedSessionByEmail model
    """

    # FIXME: REFACTOR: refactor this (if needed)
    def all_my_shares(self, user):
        """Returns all the shares"""
        return self.for_user(user)


# FIXME: REFACTOR: change uses of `SharedAlbum` to `SharedSessionByEmail` in vies, etc.
class SharedSessionByEmail(models.Model):
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

    # REFACTOR: `studio` used to be named `user` and refer to `LuminaUser`
    studio = models.ForeignKey(Studio)

    # REFACTOR: `session` used to be named `album` and refer to `Album`
    session = models.ForeignKey(Session, related_name='shares_via_email')

    # FIXME: REFACTOR: add `shared_by`, to know who shared the album
    # shared_by = models.ForeignKey(LuminaUser)

    random_hash = models.CharField(max_length=36, unique=True)  # len(uuid4) = 36

    objects = SharedSessionByEmailManager()

    # FIXME: REFACTOR: refactor this (if needed)
    def __unicode__(self):
        return u"Session {0} shared by email to {1}".format(self.album.name, self.shared_with)

    # FIXME: REFACTOR: refactor this (if needed)
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
    """
    Manager for the ImageSelection model
    """

    # FIXME: REFACTOR: refactor this (if needed)
    def pending_image_selections(self, user):
        """
        Returns ImageSelection instances for which the customer
        has to do the selection of the images.
        """
        return self.filter(customer=user, status=ImageSelection.STATUS_WAITING)

    # FIXME: REFACTOR: refactor this (if needed)
    def all_my_accessible_imageselections(self, user):
        """
        Returns all the ImageSelection instances including those for what the user
        is the customer, and those for what the user is the owner of the album
        """
        return self.filter(Q(customer=user) | Q(album__user=user))

    # FIXME: REFACTOR: refactor this (if needed)
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

    # REFACTOR: `studio` used to be named `user` and refer to `LuminaUser`
    studio = models.ForeignKey(Studio, related_name='+')

    # REFACTOR: `session` used to be named `album` and refer to `Album`
    session = models.ForeignKey(Session)

    # REFACTOR: `customer` used to refer to `LuminaUser`
    customer = models.ForeignKey(Customer, related_name='+')

    image_quantity = models.PositiveIntegerField()
    status = models.CharField(max_length=1, choices=STATUS, default=STATUS_WAITING)
    selected_images = models.ManyToManyField('Image', blank=True)

    objects = ImageSelectionManager()

    # FIXME: REFACTOR: refactor this (if needed)
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
    """
    Manager for the Image model
    """

    def visible_images(self, user):
        """Returns the images the user can see"""
        # FIXME: REFACTOR: add support for shared sessions & any other stuff
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            return self.filter(session_customer=user.user_for_customer)
        else:
            raise(Exception("User isn't PHOTOG. neither CUSTOMER - user: {}".format(user.id)))

#      FIXME: REFACTOR: refactor this (if needed)
#     def all_my_images(self, user):
#         """Returns all the user's images"""
#         return self.for_user(user)

    # FIXME: REFACTOR: refactor this (if needed)
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

    # FIXME: REFACTOR: refactor this (if needed)
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
    """
    Represents a single image
    """
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    # See: https://docs.djangoproject.com/en/1.5/topics/files/
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300)
    size = models.PositiveIntegerField()
    original_filename = models.CharField(max_length=128)
    content_type = models.CharField(max_length=64)

    # REFACTOR: `studio` used to be named `user` and refer to `LuminaUser`
    studio = models.ForeignKey(Studio)

    # REFACTOR: `session` used to be named `album` and refer to `Album`
    session = models.ForeignKey(Session, null=True)

    objects = ImageManager()

    # FIXME: REFACTOR: refactor this (if needed)
    def __unicode__(self):
        return u"Image {0}".format(self.original_filename)

    # FIXME: REFACTOR: refactor this (if needed)
    def get_absolute_url(self):
        return reverse('image_update', kwargs={'pk': self.pk})

    # FIXME: REFACTOR: refactor this (if needed)
    def set_content_type(self, content_type):
        """Set content_type, truncating if it's too large"""
        self.content_type = content_type[0:64]

    # FIXME: REFACTOR: refactor this (if needed)
    def set_original_filename(self, filename):
        """Set original filename, truncating if it's too large"""
        self.original_filename = filename[0:128]
