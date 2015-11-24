# -*- coding: utf-8 -*-

import decimal

from django.db import models
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied, ValidationError, SuspiciousOperation
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils import timezone
from django.db.models.functions import Lower

from lumina import checks  # load checks

# py3
NoneType = type(None)


# ===============================================================================
# LuminaUser
# ===============================================================================

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
    studio = models.ForeignKey(
        'Studio', related_name='photographers', null=True, blank=True,
        verbose_name="Estudio")

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
    user_for_customer = models.ForeignKey(
        'Customer', null=True, blank=True, related_name='users', verbose_name="Cliente")

    # `phone` is used in both, customers & photographers
    phone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Teléfono")
    # `cellphone` is used in both, customers & photographers
    cellphone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Celular")

    alternative_email = models.EmailField(null=True, blank=True, verbose_name="Email alternativo")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    objects = LuminaUserManager()

    def is_photographer(self):
        """Returns True if the user is a photographer"""
        assert self.user_type in (LuminaUser.PHOTOGRAPHER, LuminaUser.CUSTOMER)
        return self.user_type == LuminaUser.PHOTOGRAPHER

    def is_for_customer(self):
        """Returns True if the user is for a customer"""
        assert self.user_type in (LuminaUser.PHOTOGRAPHER, LuminaUser.CUSTOMER)
        return self.user_type == LuminaUser.CUSTOMER

    def all_my_customers(self):
        """Returns queryset of Customer"""
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return Customer.objects.customers_of(self)

    def all_my_shared_sessions_by_email(self):
        """Returns queryset of S"""
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return SharedSessionByEmail.objects.filter(studio=self.studio)

    def get_users_of_customer(self, customer_id):
        """
        Returns the users from the Customer with id = customer_id
        """
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return LuminaUser.objects.filter(user_type=LuminaUser.CUSTOMER,
                                         user_for_customer=customer_id,
                                         user_for_customer__studio=self.studio)

    def get_all_users_of_customers(self):
        """
        Returns all the CUSTOMERS users of the Studio of the user
        """
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return LuminaUser.objects.filter(user_type=LuminaUser.CUSTOMER,
                                         user_for_customer__studio=self.studio)

    def get_all_photographers(self):
        """
        Returns all the PHOTOGRAPHERS users of the Studio of the user
        """
        assert self.user_type == LuminaUser.PHOTOGRAPHER
        return LuminaUser.objects.filter(user_type=LuminaUser.PHOTOGRAPHER,
                                         studio=self.studio)

    def get_customer_types(self, **kwargs):
        """Filter using CustomerType.objects.for_photographer_ordered()

        Pass the **kwargs
        """
        return CustomerType.objects.for_photographer_ordered(self, **kwargs)

    def get_session_types(self, **kwargs):
        """Filter using SessionType.objects.for_photographer_ordered()

        Pass the **kwargs
        """
        return SessionType.objects.for_photographer_ordered(self, **kwargs)

    def get_preview_sizes(self, **kwargs):
        """Filter using PreviewSize.objects.for_photographer_ordered()

        Pass the **kwargs
        """
        return PreviewSize.objects.for_photographer_ordered(self, **kwargs)

    def get_or_create_user_preferences(self):
        try:
            return self.preferences
        except UserPreferences.DoesNotExist:
            UserPreferences.objects.create(user=self)
            return self.preferences

    def _check(self):
        if self.is_photographer():
            assert self.studio is not None, "Photographer does NOT have a studio"
        elif self.is_for_customer():
            assert self.studio is None, "Client DOES HAVE a studio"
        else:
            assert False, "TIPO INVALIDO DE USUARIO"

    def __str__(self):
        return "{} ({})".format(self.get_full_name(), self.username)


# ===============================================================================
# UserPreference
# ===============================================================================

class UserPreferences(models.Model):
    send_emails = models.BooleanField(default=True, verbose_name="Enviar emails")
    user = models.OneToOneField(LuminaUser, related_name='preferences')

    def __str__(self):
        if self.user:
            return "User preferences for {}".format(self.user.get_full_name())
        else:
            return "User preferences (no user)"


# ===============================================================================
# Studio
# ===============================================================================

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
    name = models.CharField(max_length=100, verbose_name="Nombre del estudio")
    default_terms = models.TextField(verbose_name="Términos y condiciones por default")
    watermark_text = models.CharField(max_length=40, default='', verbose_name="Marca de agua")

    objects = StudioManager()

    def __str__(self):
        return "Studio {0}".format(self.name)


# ===============================================================================
# Customer
# ===============================================================================

class CustomerManager(models.Manager):
    """
    Manager for the Customer model
    """

    def customers_of(self, photographer):
        """
        Returns the customers of the photographer's studio
        """
        return self.filter(studio=photographer.studio)


IVA_RESPONSABLE_INSCRIPTO = 'R'
IVA_RESPONSABLE_MONOTRIBUTO = 'M'
IVA_RESPONSABLE_EXCENTO = 'E'
IVA_CONSUMIDOR_FINAL = 'F'

IVA_TYPES = (
    (IVA_RESPONSABLE_INSCRIPTO, "Responsable Inscripto"),
    (IVA_RESPONSABLE_MONOTRIBUTO, "Responsable Monotributo"),
    (IVA_RESPONSABLE_EXCENTO, "Responsable Excento"),
    (IVA_CONSUMIDOR_FINAL, "Consumidor Final"),
)


class Customer(models.Model):
    """
    A Customer (as the organization that pay to the photographer).

    A customer has many 'users'... all of them are employee of the Customer,
    or any person that the customer allowed to access the images.
    """
    name = models.CharField(max_length=100, verbose_name="nombre")
    studio = models.ForeignKey(Studio, related_name='customers', verbose_name="estudio")

    customer_type = models.ForeignKey(
        'CustomerType', null=True, related_name='+', verbose_name="tipo de cliente")

    # Customer additional information (contact, biling, etc.)
    address = models.TextField(blank=True, verbose_name="dirección")
    phone = models.CharField(max_length=20, blank=True, verbose_name="teléfono")

    # company_name = models.TextField(blank=True)
    # address = models.TextField(blank=True)

    # https://github.com/yourlabs/django-cities-light
    # city = models.ForeignKey('cities_light.City', blank=True, null=True)
    city = models.CharField(max_length=40, blank=True, null=True, verbose_name="ciudad")

    cuit = models.CharField(max_length=13, blank=True, null=True)

    iva = models.CharField(max_length=1, choices=IVA_TYPES, default=None,
                           blank=True, null=True)

    ingresos_brutos = models.CharField(max_length=20, blank=True, null=True)

    notes = models.TextField(blank=True, null=True, verbose_name="Notas")

    objects = CustomerManager()

    def __str__(self):
        return self.name


# ===============================================================================
# Session
# ===============================================================================

class SessionManager(models.Manager):
    """
    Manager for the Session model
    """

    def modificable_sessions(self, user):
        """
        Returns the sessions the user can modify
        """
        if user.is_photographer():
            return self.filter(studio=user.studio)
        return self.none()

    def visible_sessions(self, user):
        """
        Returns the sessions the user can see (this means, this method
        may return sessions the user can see but not modify)
        """
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            return self.filter(shared_with=user.user_for_customer)
            # Don't include ImageSelection
            # return self.filter(Q(shared_with=user.user_for_customer) |
            #                    Q(imageselection__customer=user.user_for_customer)
            #                    ).distinct()
        else:
            raise Exception("User isn't PHOTOG. neither CUSTOMER - user: {}".format(user.id))

    def get_pending_uploads(self, user):
        """
        Returns the sessions that have pending uploads.
        """
        # FIXME: Implement this!
        return self.modificable_sessions(user)


# FIXME: REFACTOR: change uses of `Album` to `Session` in views, etc.
class Session(models.Model):
    """
    Represents a photo session.
    """
    name = models.CharField(max_length=300, verbose_name="Nombre")

    studio = models.ForeignKey(Studio, verbose_name="estudio")
    photographer = models.ForeignKey(LuminaUser, verbose_name="fotógrafo")
    customer = models.ForeignKey(Customer, null=False, blank=False, verbose_name="cliente")

    session_type = models.ForeignKey('SessionType', related_name='+', verbose_name="tipo de sesión")

    shared_with = models.ManyToManyField(
        Customer, blank=True, related_name='sessions_shared_with_me',
        verbose_name="Compartida con")

    worked_hours = models.PositiveIntegerField(default=0, verbose_name="horas trabajadas")

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    archived = models.BooleanField(default=False, verbose_name="Archivada")

    album_icon = models.ForeignKey('Image', blank=True, null=True, related_name='+')

    objects = SessionManager()

    def clean(self):
        # Check if customer is OK. IE: customer should be the same as the
        # customers pointing to any of the existing quotes
        quotes_pointing_to_self = SessionQuote.objects.filter(session=self).all()
        for a_quote in quotes_pointing_to_self:
            if a_quote.customer.id != self.customer.id:
                raise ValidationError('Ha seleccionado un cliente distinto al del presupuesto')

    def __str__(self):
        return "Session {0}".format(self.name)

    def get_absolute_url(self):
        return reverse('session_detail', kwargs={'pk': self.pk})

    def archive(self, user):
        """
        Archive the session
        """
        assert user.is_photographer()
        assert self.studio == user.studio
        assert not self.archived
        self.archived = True
        self.save(force_update=True, update_fields=['archived'])

    def unarchive(self, user):
        """
        Un-archive the session
        """
        assert user.is_photographer()
        assert self.studio == user.studio
        assert self.archived
        self.archived = False
        self.save(force_update=True, update_fields=['archived'])

    def get_active_quote(self):
        """
        This method returns the quote associated to this session.

        This is kept for historical reasons, and could be removed in the future,
        since right now, if the quote is canceled, there is NO WAY to create
        a new version associated to the existing session.
        """
        # return self.quotes.filter(exclude=XXXX).get()
        return self.quotes.get()

    def set_image_as_album_icon(self, image):
        assert isinstance(image, Image)
        self.album_icon = image
        self.save()


# ===============================================================================
# SharedSessionByEmail
# ===============================================================================

class SharedSessionByEmailManager(models.Manager):
    """
    Manager for the SharedSessionByEmail model
    """


# FIXME: REFACTOR: change uses of `SharedAlbum` to `SharedSessionByEmail` in vies, etc.
class SharedSessionByEmail(models.Model):
    """
    Represents a session shared via email.

    An email is sent to the receiver, with a link to view the album.
    To view the almbum, the receiver just need the link, and doens't
    need to have an account nor bie logged in.

    Anyone with the link can see tha images of the album.

    With the current implementation, all the images of the album
    can be seen, and downloaded.
    """
    shared_with = models.EmailField(max_length=254, verbose_name="compartida con")
    # https://docs.djangoproject.com/en/1.5/ref/models/fields/#emailfield

    studio = models.ForeignKey(Studio, verbose_name="estudio")

    session = models.ForeignKey(Session, related_name='shares_via_email', verbose_name="sesión")

    random_hash = models.CharField(max_length=36, unique=True)  # len(uuid4) = 36

    objects = SharedSessionByEmailManager()

    def __str__(self):
        return "Session {0} shared by email to {1}".format(self.session.name, self.shared_with)

    def get_image_from_session(self, image_id):
        """
        Returns the image with 'id' = 'image_id' only
        if the image is part of the SharedSessionByEmail.
        """
        try:
            return self.session.image_set.get(pk=image_id)
        except Image.DoesNotExist:
            raise(PermissionDenied("The Image {0} doesn't belong to "
                                   "the SharedSessionByEmail {1}"
                                   " or doesn't exists".format(image_id, self.id)))


# ===============================================================================
# ImageSelection
# ===============================================================================

class ImageSelectionManager(models.Manager):
    """
    Manager for the ImageSelection model
    """

    def all_my_accessible_imageselections(self, user):
        """
        Returns all the ImageSelection instances including those for what the user
        is the customer, and those for what the user is the owner of the album
        """
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            return self.filter(session__customer=user.user_for_customer)
        raise SuspiciousOperation()

    def pending_image_selections(self, user):
        """
        Returns ImageSelection instances for which the customer
        has to do the selection of the images.
        """
        assert user.is_for_customer()
        return self.filter(customer=user.user_for_customer, status=ImageSelection.STATUS_WAITING)

    def all_my_imageselections_awaiting_selection_as_customer(self, user):
        """
        Returns a queryset filtering the ImageSelections awaiting for the customer to select the images.
        """
        assert user.is_for_customer()
        return self.filter(customer=user.user_for_customer,
                           status=ImageSelection.STATUS_WAITING)

    def all_my_available_imageselections_as_customer(self, user):
        """
        Returns a queryset filtering the ImageSelections available for customer.
        """
        assert user.is_for_customer()
        return self.filter(customer=user.user_for_customer,
                           status=ImageSelection.STATUS_IMAGES_SELECTED,
                           session__archived=False)

    def all_my_imageselections_awaiting_selection_as_photographer(self, user):
        """
        Returns a queryset filtering the ImageSelections awaiting for the customer to select the images.
        """
        assert user.is_photographer()
        return self.filter(studio=user.studio,
                           status=ImageSelection.STATUS_WAITING)

    def full_quality_pending_uploads(self, user):
        """
        Returns ImageSelection instances which user has selected the images,
        but has at least one images that doesn't have the full-quality version.
        """
        assert user.is_photographer()
        return self.filter(studio=user.studio,
                           status=ImageSelection.STATUS_IMAGES_SELECTED,
                           selected_images__image='').distinct()


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
        (STATUS_WAITING, 'Esperando selección de cliente'),
        (STATUS_IMAGES_SELECTED, 'Seleccion realizada'),
    )

    studio = models.ForeignKey(Studio, related_name='+', verbose_name="estudio")

    session = models.ForeignKey(Session, verbose_name="sesión")

    customer = models.ForeignKey(Customer, related_name='+', verbose_name="cliente")

    image_quantity = models.PositiveIntegerField(verbose_name="cantidad de imágenes")
    status = models.CharField(max_length=1, choices=STATUS, default=STATUS_WAITING, verbose_name="estado")
    selected_images = models.ManyToManyField('Image', blank=True, verbose_name="imágenes seleccionadas")

    # FIXME: `ImageSelection.preview_size` maybe should be non-null
    preview_size = models.ForeignKey('PreviewSize', null=True, verbose_name="tamaño de previsualización")

    quote = models.ForeignKey('SessionQuote', null=True, blank=True, verbose_name="presupuesto")

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = ImageSelectionManager()

    def __str__(self):
        return "ImageSelection for session {0}".format(self.session.name)

    def get_selected_images_without_full_quality(self):
        return self.selected_images.filter(image='')

    def clean(self):
        if self.id is None and self.image_quantity:
            # --- NEW INSTANCE! And user has specified `image_quantity` ---
            # Check: image_quantity can't be greater than the number of images of the session
            image_count = self.session.image_set.count()
            if self.image_quantity > image_count:
                if image_count == 0:
                    msg = {'image_quantity': 'La sesión fotográfica no posee imágenes'.format(image_count)}
                else:
                    msg = {'image_quantity': 'Debe seleccionar {} o menos imagenes'.format(image_count)}
                raise ValidationError(msg)


# ===============================================================================
# Image
# ===============================================================================

class ImageManager(models.Manager):
    """
    Manager for the Image model
    """

    def visible_images(self, user):
        """Returns the images the user can see"""
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            # FIXME: REFACTOR: add support for shared sessions & any other stuff
            return self.filter(session__customer=user.user_for_customer)
        else:
            raise Exception("User isn't PHOTOG. neither CUSTOMER - user: {}".format(user.id))

    # ===============================================================================
    #     # F-I-X-M-E: REFACTOR: refactor this (if needed)
    #     def all_previsualisable(self, user):
    #         """
    #         Returns all the visible images for preview, ie: thumbnails or low quality.
    #
    #         Some of the images may be downloaded (in full resolution).
    #         (ie: the user's images + the images of shared albums of other users)
    #         but other won't be downloadable (images from ImageSelection)
    #         """
    #         q = Q(user=user)
    #         q = q | Q(album__shared_with=user)
    #         q = q | Q(album__imageselection__customer=user)
    #         return self.filter(q).distinct()
    # ===============================================================================

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

        if user.is_photographer():
            try:
                # If the image is from the same studio, return it
                return self.get(studio=user.studio, id=image_id)
            except Image.DoesNotExist:
                pass

        if user.is_for_customer():
            try:
                # If the image if from a shared session, return it
                return self.get(session__shared_with=user.user_for_customer, id=image_id)

            except Image.DoesNotExist:
                pass

            # Tha image was selected by the user?
            return self.filter(imageselection__customer=user.user_for_customer,
                               imageselection__status=ImageSelection.STATUS_IMAGES_SELECTED,
                               imageselection__selected_images=image_id).distinct().get(id=image_id)

        raise Exception()


class Image(models.Model):
    """
    Represents a single image
    """
    # See: https://docs.djangoproject.com/en/1.5/ref/models/fields/#filefield
    # See: https://docs.djangoproject.com/en/1.5/topics/files/
    image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300, verbose_name="imagen", null=True, blank=True)
    size = models.PositiveIntegerField(verbose_name="tamaño", null=True, blank=True)
    original_filename = models.CharField(max_length=128, verbose_name="nombre de archivo original",
                                         null=True, blank=True)
    content_type = models.CharField(max_length=64, verbose_name="tipo de contenido", null=True, blank=True)

    thumbnail_image = models.FileField(upload_to='images/%Y/%m/%d', max_length=300,
                                       verbose_name="previsualizacion", null=True, blank=True)
    thumbnail_size = models.PositiveIntegerField(verbose_name="tamaño de la previsualizacion", null=True, blank=True)
    thumbnail_original_filename = models.CharField(max_length=128,
                                                   verbose_name="nombre de archivo (en cliente) de previsualizacion",
                                                   null=True, blank=True)
    thumbnail_content_type = models.CharField(max_length=64,
                                              verbose_name="tipo de contenido de previsualizacion",
                                              null=True, blank=True)
    original_file_checksum = models.CharField(max_length=64,
                                              verbose_name="checksum de archivo original",
                                              null=True, blank=True)

    studio = models.ForeignKey(Studio, verbose_name="estudio")

    # FIXME: why Image.session could be 'null'?
    session = models.ForeignKey(Session, null=True, verbose_name="sesión")

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    objects = ImageManager()

    def get_image_or_thumbnail_file(self):
        if self.image:
            return self.image
        else:
            return self.thumbnail_image

    def __str__(self):
        if self.image:
            return "Image {0}".format(self.image)
        else:
            return "Image {0} (thumb-only)".format(self.thumbnail_image)

    def get_absolute_url(self):
        return reverse('image_update', kwargs={'pk': self.pk})

    def set_content_type(self, content_type):
        """Set content_type, truncating if it's too large"""
        self.content_type = content_type[0:64]

    def set_original_filename(self, filename):
        """Set original filename, truncating if it's too large"""
        self.original_filename = filename[0:128]

    def set_thumbnail_content_type(self, content_type):
        """Set content_type, truncating if it's too large"""
        self.thumbnail_content_type = content_type[0:64]

    def set_thumbnail_original_filename(self, filename):
        """Set original filename for thumb, truncating if it's too large"""
        self.thumbnail_original_filename = filename[0:128]

    def get_original_filename_or_thumbnail_original_filename(self):
        return self.original_filename or self.thumbnail_original_filename

    def get_thumb_64x64_url(self):
        return reverse('image_thumb_64x64', args=[self.id])

    def get_thumb_200x200_url(self):
        return reverse('image_thumb_200x200', args=[self.id])

    def full_quality_available(self):
        return bool(self.image)


# ===============================================================================
# SessionQuote
# ===============================================================================

class SessionQuoteManager(models.Manager):
    """
    Manager for the SessionQuote model
    """

    def visible_sessionquote(self, user):
        """
        Returns the quotes the user can see (this means, this method
        may return sessions the user can see but not modify)
        """
        if user.is_photographer():
            return self.filter(studio=user.studio)
        elif user.is_for_customer():
            return self.filter(customer=user.user_for_customer,
                               status__in=[SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE,
                                           SessionQuote.STATUS_ACCEPTED,
                                           SessionQuote.STATUS_REJECTED])
        else:
            raise Exception("User isn't PHOTOG. neither CUSTOMER - user: {}".format(user.id))

    def modificable_sessionquote(self, user):
        """
        Returns the sessions the user can modify. By modifications I mean changing the fields
        values using a *form*. IE: calling `modificable_sessionquote()` with a customer will
        return an EMPTY result, since customers can't modify quotes using form.

        Customers can modify quote instances with accept()/reject(), but since this case does not
        uses forms, this method won't return that instances.
        """
        if user.is_photographer():
            valid_statuses = (SessionQuote.STATUS_QUOTING,
                              SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE,
                              SessionQuote.STATUS_ACCEPTED)
            return self.filter(studio=user.studio, status__in=valid_statuses)
        return self.none()

    def get_waiting_for_customer_response(self, user):
        """
        Returns SessionQuotes in STATUS_WAITING_CUSTOMER_RESPONSE for the user.
        """
        assert user.is_for_customer()
        return self.filter(customer=user.user_for_customer,
                           status=SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)


class SessionQuote(models.Model):
    STATUS_QUOTING = 'Q'
    STATUS_WAITING_CUSTOMER_RESPONSE = 'S'
    STATUS_ACCEPTED = 'A'
    STATUS_REJECTED = 'R'
    STATUS_CANCELED = 'E'
    STATUS = (
        (STATUS_QUOTING, 'Siendo creado por fotografo'),
        (STATUS_WAITING_CUSTOMER_RESPONSE, 'Esperando aceptacion de cliente'),
        (STATUS_ACCEPTED, 'Aceptado por el cliente'),
        (STATUS_REJECTED, 'Rechazado por el cliente'),
        (STATUS_CANCELED, 'Cancelado por fotografo'),
    )

    name = models.CharField(max_length=300, verbose_name="nombre")
    studio = models.ForeignKey(Studio, related_name='session_quotes', verbose_name="estudio")
    customer = models.ForeignKey(Customer, related_name='session_quotes', verbose_name="cliente")
    image_quantity = models.PositiveIntegerField(verbose_name="cantidad de imágenes")
    status = models.CharField(
        max_length=1, choices=STATUS, default=STATUS_QUOTING, verbose_name="estado")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="costo")
    terms = models.TextField(verbose_name="términos")
    accepted_rejected_by = models.ForeignKey(LuminaUser, related_name='+', null=True, blank=True)
    accepted_rejected_at = models.DateTimeField(null=True, blank=True)
    accepted_quote_alternative = models.ForeignKey('SessionQuoteAlternative',
                                                   related_name='+',
                                                   on_delete=models.PROTECT,
                                                   null=True, blank=True,
                                                   verbose_name="presupuesto alternativo")

    stipulated_date = models.DateField(verbose_name="fecha de entrega pactada")

    stipulated_down_payment = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="entrega inicial pactada")
    #    actual_down_payment = models.DecimalField(max_digits=10, decimal_places=2,
    #        verbose_name="entrega inicial realizada")

    session = models.ForeignKey(
        Session, related_name='quotes', null=True, blank=True, verbose_name="Sesión", on_delete=models.SET_NULL)

    created = models.DateTimeField(auto_now_add=True)
    last_modified = models.DateTimeField(auto_now=True)

    archived = models.BooleanField(default=False, verbose_name="Archivado")

    objects = SessionQuoteManager()

    def confirm(self, user):
        """
        The phtographer confirms the quote, and it is sent to the client
        to be accepted (or rejected).
        """
        assert user.is_photographer()
        assert user.studio == self.studio
        assert self.status == SessionQuote.STATUS_QUOTING
        self.status = SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE
        self.save()

    def cancel(self, user):
        """
        The phtographer cancels the quote.
        """
        assert user.is_photographer()
        assert user.studio == self.studio
        assert self.status in (SessionQuote.STATUS_QUOTING,
                               SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE,
                               SessionQuote.STATUS_ACCEPTED,)
        self.status = SessionQuote.STATUS_CANCELED
        self.save()

    def original_quote_is_accepted(self):
        """Returns True if the original quote was accepted (and NOT a SessionQuoteAlternative)"""
        if self.status in [SessionQuote.STATUS_ACCEPTED,
                           SessionQuote.STATUS_CANCELED]:
            if self.accepted_quote_alternative is None:
                return True
        return False

    def accept(self, user, alternative_id=None):
        """
        The customer accept the quote.

        If `alternative_id` is None, the original quote is accepted.
        """
        assert user.is_for_customer()
        assert user.user_for_customer == self.customer
        assert user.user_for_customer.studio == self.studio
        assert self.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE

        if alternative_id is not None:
            assert isinstance(alternative_id, int)
            sqa = SessionQuoteAlternative.objects.get(pk=alternative_id, session_quote=self)
            assert self.accepted_quote_alternative is None
            self.accepted_quote_alternative = sqa

        # change state after checks
        self.status = SessionQuote.STATUS_ACCEPTED
        self.accepted_rejected_by = user
        self.accepted_rejected_at = timezone.now()

        self.save()

    def update_quote_alternative(self, user, alternative_id):
        """
        The customer change the selected alternative quote.
        """
        assert user.is_for_customer()
        assert user.user_for_customer == self.customer
        assert user.user_for_customer.studio == self.studio
        assert self.status == SessionQuote.STATUS_ACCEPTED
        assert isinstance(alternative_id, int)

        sqa = self.quote_alternatives.get(pk=alternative_id)
        self.accepted_quote_alternative = sqa

        # change state after checks
        self.accepted_rejected_by = user
        self.accepted_rejected_at = timezone.now()

        self.save()

    def reject(self, user):
        """
        The customer accept the quote.
        """
        assert user.is_for_customer()
        assert user.user_for_customer == self.customer
        assert user.user_for_customer.studio == self.studio
        assert self.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE
        self.status = SessionQuote.STATUS_REJECTED
        self.accepted_rejected_by = user
        self.accepted_rejected_at = timezone.now()
        self.save()

    def get_selected_quote_values(self):
        """
        Returns a pair of values: (image quantity, cost),
        from the selected quote.

        This method should only be called for STATUS_ACCEPTED quotes!
        """
        assert self.status == self.STATUS_ACCEPTED

        if self.accepted_quote_alternative:
            return (self.accepted_quote_alternative.image_quantity,
                    self.accepted_quote_alternative.cost)
        else:
            return (self.image_quantity,
                    self.cost)

    def get_quote_values_for_display(self):
        """
        Returns a pair of values: (image quantity, cost) to be shown to the user.
        This method is used in the UI, to display image quantity and cost associated to the quote.

        In some cases, this method should return the original quote, but if an alternative was selected,
        this method should return the values from the alternative.

        This method ignores the state of the quote, since ALWAYS should return something to show.
        """
        # This is VERY similar to `get_selected_quote_values()`, but let's keep them separated....
        if self.accepted_quote_alternative:
            return (self.accepted_quote_alternative.image_quantity,
                    self.accepted_quote_alternative.cost)
        else:
            return (self.image_quantity,
                    self.cost)

    def get_valid_alternatives(self):
        """
        Return availables alternatives that a customer can choose.
        """
        quote_alternatives_qs = self.quote_alternatives.all().order_by('image_quantity')
        if self.status == self.STATUS_WAITING_CUSTOMER_RESPONSE:
            # The customer hasn't choosed any alternative. Show'em all
            return quote_alternatives_qs

        elif self.status == self.STATUS_ACCEPTED:
            if self.original_quote_is_accepted():
                # Original quote selected. Show all the alternatives
                return quote_alternatives_qs

            # The customer has choosed an alternative. Show the alternatives with
            #  more photos than the current alternative
            assert self.accepted_quote_alternative is not None
            current_quantity = self.accepted_quote_alternative.image_quantity
            return quote_alternatives_qs.filter(image_quantity__gt=current_quantity)

        else:
            raise Exception("Invalid state: {}".format(self.status))

    def status_is_accepted(self):
        return self.status == self.STATUS_ACCEPTED

    def __str__(self):
        return "Quote for {}".format(self.customer)


class SessionQuoteAlternative(models.Model):
    session_quote = models.ForeignKey(
        SessionQuote, related_name='quote_alternatives', verbose_name="presupuesto")
    image_quantity = models.PositiveIntegerField(verbose_name="cantidad de imágenes")
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="costo")

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session_quote", "image_quantity")
        ordering = ["image_quantity"]

    def is_selected(self):
        """Returns True if 'self' represent the alternative selected by the customer"""
        if self.session_quote.accepted_quote_alternative:
            return bool(self.id == self.session_quote.accepted_quote_alternative.id)
        return False

    def __str__(self):
        return "SessionQuoteAlternative for quote {0} ({1} photos, $ {2})".format(
            self.session_quote, self.image_quantity, self.cost)


# ===============================================================================
# CustomerType
# ===============================================================================

class CustomerTypeManager(models.Manager):

    def for_photographer_ordered(self, photographer, exclude_archived=False):
        """Return CustomerType visible for photographer"""
        assert photographer.is_photographer()
        qs = self.filter(studio=photographer.studio)
        if exclude_archived:
            qs = qs.filter(archived=False)
        return qs.order_by(Lower('name'))


class CustomerType(models.Model):
    name = models.CharField(max_length=100, verbose_name="nombre")
    studio = models.ForeignKey('Studio', related_name='customer_types', verbose_name="estudio")
    archived = models.BooleanField(default=False, verbose_name="Archivado")

    objects = CustomerTypeManager()

    class Meta:
        unique_together = ("studio", "name")
        verbose_name = "tipo de cliente"
        verbose_name_plural = "tipos de cliente"

    def __str__(self):
        return self.name


# ===============================================================================
# SessionType
# ===============================================================================

class SessionTypeManager(models.Manager):

    def for_photographer_ordered(self, photographer, exclude_archived=False):
        """Return SessionType visible for photographer"""
        assert photographer.is_photographer()
        qs = self.filter(studio=photographer.studio)
        if exclude_archived:
            qs = qs.filter(archived=False)
        return qs.order_by(Lower('name'))


class SessionType(models.Model):
    name = models.CharField(max_length=100, verbose_name="nombre")
    studio = models.ForeignKey('Studio', related_name='session_types', verbose_name="estudio")
    archived = models.BooleanField(default=False, verbose_name="Archivado")

    objects = SessionTypeManager()

    class Meta:
        unique_together = ("studio", "name")
        verbose_name = "tipo de sesión"
        verbose_name_plural = "tipos de sesión"

    def __str__(self):
        return self.name


# ===============================================================================
# PreviewSize
# ===============================================================================

class PreviewSizeManager(models.Manager):

    def for_photographer_ordered(self, photographer, exclude_archived=False):
        """Return SessionType visible for photographer"""
        assert photographer.is_photographer()
        qs = self.filter(studio=photographer.studio)
        if exclude_archived:
            qs = qs.filter(archived=False)
        return qs.order_by('max_size')


class PreviewSize(models.Model):
    max_size = models.PositiveIntegerField(verbose_name="Tamaño máximo")
    studio = models.ForeignKey('Studio', related_name='preview_sizes', verbose_name="estudio")
    archived = models.BooleanField(default=False, verbose_name="Archivado")

    objects = PreviewSizeManager()

    class Meta:
        unique_together = ("max_size", "studio")
        verbose_name = "tamaño de previsualización"
        verbose_name_plural = "tamaños de previsualización"
        ordering = ["max_size"]

    def __str__(self):
        return "{0}x{0}".format(self.max_size)
