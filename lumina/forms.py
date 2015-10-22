# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy
from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout
from localflavor.ar.forms import ARCUITField

from lumina import models
from lumina import forms_utils
from lumina.models import LuminaUser, Customer, SharedSessionByEmail, \
    Image, ImageSelection, UserPreferences, SessionType


# ===============================================================================
# CustomAuthenticationForm
# ===============================================================================

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = "login"
        # self.helper.form_class = 'xxx-form-horizontal'
        # self.helper.label_class = 'xxx-helper-label_class'
        # self.helper.field_class = 'xxx-helper-field_class'
        self.helper.layout = helper.Layout(
            layout.Fieldset(
                'Inicio de sesión',
                'username',
                'password',
                layout.Hidden('next', '{{next}}'),
            ),
            bootstrap.FormActions(
                layout.Submit('submit', 'Iniciar sesión'),
            ),
        )


# ===============================================================================
# SharedSessionByEmail
# ===============================================================================

class SharedSessionByEmailCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session')

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                'Compartir sesión por email',
                'shared_with',
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Compartir', css_id='form-submit-button'),
            ),
        )

        assert isinstance(session, models.Session)
        self.instance.session = session

    class Meta:
        model = SharedSessionByEmail
        fields = ('shared_with',)


# ===============================================================================
# ImageSelection
# ===============================================================================

class ImageSelectionCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        photographer = kwargs.pop('photographer')
        session = kwargs.pop('session')

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                'Creación de solicitud de imágenes',
                'image_quantity',
                'preview_size',
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Crear solicitud', css_id='form-submit-button'),
            ),
        )

        assert isinstance(photographer, LuminaUser)
        assert photographer.is_photographer()

        assert isinstance(session, models.Session)

        self.instance.session = session

        self.fields['preview_size'].queryset = models.PreviewSize.objects.for_photographer_ordered(photographer)

    def clean_image_quantity(self):
        data = self.cleaned_data['image_quantity']
        if data <= 0:
            raise forms.ValidationError("La cantidad de imagenes debe ser mayor a 0")

        # Always return the cleaned data, whether you have changed it or not.
        return data

    class Meta:
        model = ImageSelection
        fields = ('image_quantity', 'preview_size')


class ImageSelectionAutoCreateForm(forms.ModelForm):

    def clean_preview_size(self):
        preview_size = self.cleaned_data['preview_size']
        if not preview_size:
            raise forms.ValidationError("Debe seleccionar un tamaño de visualizacion")

        return preview_size

    class Meta:
        model = ImageSelection
        fields = ('preview_size',)
        # exclude = ('user', 'status', 'selected_images')


# ===============================================================================
# Session
# ===============================================================================

class _GenericSessionForm(forms_utils.GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('session_list')
    FIELDS = ['name', 'session_type', 'photographer', 'customer', 'worked_hours']

    def __init__(self, *args, **kwargs):
        photographer = kwargs.pop('photographer')

        super().__init__(*args, **kwargs)

        assert isinstance(photographer, LuminaUser)
        assert photographer.is_photographer()

        self.fields['session_type'].queryset = photographer.get_session_types()
        self.fields['photographer'].queryset = photographer.get_all_photographers()
        self.fields['customer'].queryset = Customer.objects.customers_of(photographer)

    class Meta:
        model = models.Session
        fields = ('name', 'session_type', 'photographer', 'customer', 'worked_hours')


class SessionCreateForm(_GenericSessionForm):
    FORM_TITLE = 'Crear nueva sesión fotográfica'
    SUBMIT_LABEL = 'Crear'


class SessionUpdateForm(_GenericSessionForm):
    FORM_TITLE = 'Actualizar sesión fotográfica'
    SUBMIT_LABEL = 'Guardar'


class SessionCreateFromQuoteForm(forms_utils.GenericCreateUpdateModelForm):
    """When creating a sessoin from a QUOTE, some field should not be shown"""

    FIELDS = ['name', 'session_type', 'photographer', 'worked_hours']

    FORM_TITLE = 'Crear nueva sesión fotográfica'
    SUBMIT_LABEL = 'Crear'

    def __init__(self, *args, **kwargs):
        self.quote = kwargs.pop('quote')
        self.user = kwargs.pop('user')
        assert isinstance(self.quote, models.SessionQuote)
        assert isinstance(self.user, models.LuminaUser)
        super().__init__(*args, **kwargs)
        self.fields['session_type'].queryset = self.user.get_session_types()
        self.fields['photographer'].queryset = self.user.get_all_photographers()

    def get_cancel_url(self):
        return reverse_lazy('quote_detail', args=[self.quote.id])

    class Meta:
        model = models.Session
        fields = ('name', 'session_type', 'photographer', 'worked_hours')


class SessionSearchForm(forms.Form):

    ARCHIVED_STATUS_ALL = 'ALL'
    ARCHIVED_STATUS_ARCHIVED = 'ARCHIVED'
    ARCHIVED_STATUS_ACTIVE = 'ACTIVE'

    ARCHIVED_STATUS_CHOICES = (
        (ARCHIVED_STATUS_ALL, 'Todas'),
        (ARCHIVED_STATUS_ARCHIVED, 'Archivadas'),
        (ARCHIVED_STATUS_ACTIVE, 'Activas'),
    )
    archived_status = forms.ChoiceField(choices=ARCHIVED_STATUS_CHOICES,
                                        widget=forms.RadioSelect,
                                        initial=ARCHIVED_STATUS_ALL,
                                        label='Archivadas',
                                        required=False)
    fecha_creacion_desde = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (desde)")
    fecha_creacion_hasta = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (hasta)")
    customer = forms.ModelChoiceField(Customer.objects.none(),
                                      empty_label='Todos los clientes',
                                      label='Cliente',
                                      required=False)
    session_type = forms.ModelChoiceField(SessionType.objects.none(),
                                          empty_label='Todos los tipos de sesiones',
                                          label='Tipo de sesión',
                                          required=False)
    page = forms.CharField(max_length=5, required=False, widget=forms.HiddenInput)

    def __init__(self, photographer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = 'session_search'
        self.helper.form_id = 'form-session-search'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            bootstrap.InlineRadios('archived_status'),
            forms_utils.DatePickerField('fecha_creacion_desde'),
            forms_utils.DatePickerField('fecha_creacion_hasta'),
            'customer',
            'session_type',
            'page',
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
            ),
        )

        assert isinstance(photographer, LuminaUser)
        assert photographer.is_photographer()
        self.fields['customer'].queryset = Customer.objects.customers_of(photographer)
        self.fields['session_type'].queryset = SessionType.objects.for_photographer_ordered(photographer)

    def clean(self):
        cleaned_data = super().clean()
        fecha_creacion_desde = cleaned_data.get("fecha_creacion_desde")
        fecha_creacion_hasta = cleaned_data.get("fecha_creacion_hasta")

        if fecha_creacion_desde and fecha_creacion_hasta:
            if fecha_creacion_desde > fecha_creacion_hasta:
                msg = "'Fecha de creacion (desde)' debe ser anterior a 'Fecha de creacion (hasta)'"
                self.add_error('fecha_creacion_desde', msg)
                self.add_error('fecha_creacion_hasta', msg)


# ===============================================================================
# Image
# ===============================================================================

class ImageCreateForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        session = kwargs.pop('session')

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                'Agregar imágenes a la sesión fotográfica',
                'image',
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Agregar', css_id='form-submit-button'),
            ),
        )

        assert isinstance(session, models.Session)
        self.instance.session = session

    class Meta:
        model = Image
        fields = ('image',)


class ImageUpdateForm(forms.ModelForm):

    class Meta:
        model = Image
        fields = ('session',)


class ImageSearchForm(forms.Form):

    fecha_creacion_desde = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (desde)")
    fecha_creacion_hasta = forms.DateField(required=False,
                                           label='Fecha de creación',
                                           help_text="Fecha de creacion (hasta)")
    customer = forms.ModelChoiceField(Customer.objects.none(),
                                      empty_label='Todos los clientes',
                                      label='Cliente',
                                      required=False)
    session_type = forms.ModelChoiceField(SessionType.objects.none(),
                                          empty_label='Todos los tipos de sesiones',
                                          label='Tipo de sesión',
                                          required=False)
    page = forms.CharField(max_length=5, required=False, widget=forms.HiddenInput)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = 'image_list'
        self.helper.form_id = 'form-image-search'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        assert isinstance(user, LuminaUser)
        assert user.is_photographer()

        self.helper.layout = helper.Layout(
            forms_utils.DatePickerField('fecha_creacion_desde'),
            forms_utils.DatePickerField('fecha_creacion_hasta'),
            'customer',
            'session_type',
            'page',
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
            ),
        )
        self.fields['customer'].queryset = Customer.objects.customers_of(user)
        self.fields['session_type'].queryset = SessionType.objects.for_photographer_ordered(user)

    def clean(self):
        cleaned_data = super().clean()
        fecha_creacion_desde = cleaned_data.get("fecha_creacion_desde")
        fecha_creacion_hasta = cleaned_data.get("fecha_creacion_hasta")

        if fecha_creacion_desde and fecha_creacion_hasta:
            if fecha_creacion_desde > fecha_creacion_hasta:
                msg = "'Fecha de creacion (desde)' debe ser anterior a 'Fecha de creacion (hasta)'"
                self.add_error('fecha_creacion_desde', msg)
                self.add_error('fecha_creacion_hasta', msg)


# ===============================================================================
# Customer
# ===============================================================================

class _GenericCustomerForm(forms_utils.GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('customer_list')
    FIELDS = [
        'name', 'customer_type', 'address', 'phone', 'city', 'iva', 'cuit',
        'ingresos_brutos', 'notes'
    ]

    cuit = ARCUITField(max_length=13, min_length=0, required=False,
                       help_text="Formato: XX-XXXXXXXX-X")

    class Meta:
        model = models.Customer
        fields = (
            'name', 'customer_type', 'address', 'phone', 'city', 'iva', 'cuit',
            'ingresos_brutos', 'notes'
        )


class CustomerCreateForm(_GenericCustomerForm):
    FORM_TITLE = 'Crear nuevo cliente'
    SUBMIT_LABEL = 'Crear'


class CustomerUpdateForm(_GenericCustomerForm):
    FORM_TITLE = 'Actualizar cliente'
    SUBMIT_LABEL = 'Guardar'


# ===============================================================================
# CustomerType
# ===============================================================================

class _GenericCustomerTypeForm(forms_utils.GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('customer_type_list')
    FIELDS = ['name']

    class Meta:
        model = models.CustomerType
        fields = ('name',)

    def _get_validation_exclusions(self):
        # HACK to force ModelForm validate uniqueness.
        # Works in `PreviewSizeCreateForm` because we manually put `instance` kwarg
        validation_exclusions = super()._get_validation_exclusions()
        return [_ for _ in validation_exclusions if _ != 'studio']


class CustomerTypeCreateForm(_GenericCustomerTypeForm):
    FORM_TITLE = 'Crear nuevo tipo de cliente'
    SUBMIT_LABEL = 'Crear'


class CustomerTypeUpdateForm(_GenericCustomerTypeForm):
    FORM_TITLE = 'Actualizar tipo de cliente'
    SUBMIT_LABEL = 'Guardar'


# ===============================================================================
# CustomerType
# ===============================================================================

class _GenericSessionTypeForm(forms_utils.GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('session_type_list')
    FIELDS = ['name']

    class Meta:
        model = models.SessionType
        fields = ('name',)

    def _get_validation_exclusions(self):
        # HACK to force ModelForm validate uniqueness.
        # Works in `SessionTypeCreateForm` because we manually put `instance` kwarg
        validation_exclusions = super()._get_validation_exclusions()
        return [_ for _ in validation_exclusions if _ != 'studio']


class SessionTypeCreateForm(_GenericSessionTypeForm):
    FORM_TITLE = 'Crear nuevo tipo de sesión fotográfica'
    SUBMIT_LABEL = 'Crear'


class SessionTypeUpdateForm(_GenericSessionTypeForm):
    FORM_TITLE = 'Actualizar tipo de sesión fotográfica'
    SUBMIT_LABEL = 'Guardar'


# ===============================================================================
# CustomerType
# ===============================================================================

class _GenericPreviewSizeForm(forms_utils.GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('preview_size_list')
    FIELDS = ['max_size']

    class Meta:
        model = models.PreviewSize
        fields = ('max_size',)

    def _get_validation_exclusions(self):
        # HACK to force ModelForm validate uniqueness.
        # Works in `PreviewSizeCreateForm` because we manually put `instance` kwarg
        validation_exclusions = super()._get_validation_exclusions()
        return [_ for _ in validation_exclusions if _ != 'studio']


class PreviewSizeCreateForm(_GenericPreviewSizeForm):
    FORM_TITLE = 'Crear nuevo tamaño de previsualizaciones'
    SUBMIT_LABEL = 'Crear'


class PreviewSizeUpdateForm(_GenericPreviewSizeForm):
    FORM_TITLE = 'Actualizar tamaño de previsualizacion'
    SUBMIT_LABEL = 'Guardar'


# ===============================================================================
# UserPreferences
# ===============================================================================

class UserPreferencesUpdateForm(forms.ModelForm):

    # first_name = models.CharField(_('first name'), max_length=30, blank=True)
    first_name = forms.CharField(
        max_length=30, required=True,
        label='Nombre')
    # last_name = models.CharField(_('last name'), max_length=30, blank=True)
    last_name = forms.CharField(
        max_length=30, required=True,
        label='Apellido')
    # email = models.EmailField(_('email address'), blank=True)
    email = forms.EmailField(
        required=True,
        label='Correo electrónico')

    # cellphone = models.CharField(max_length=20, null=True, blank=True, verbose_name="Celular")
    cellphone = forms.CharField(
        max_length=20, required=False,
        label='Celular')

    password1 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(), label='Contrasena',
        help_text="Ingrese la nueva contraseña (si desea cambiarla)")
    password2 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(),
        label='Contrasena (otra vez)',
        help_text="Repita la nueva contraseña (si desea cambiarla)")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                'Actualizar preferencias de usuario',
                'first_name',
                'last_name',
                'email',
                'cellphone',
                'password1',
                'password2',
                'send_emails',
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Guardar', css_id='form-submit-button'),
            ),
        )

    def clean(self):
        super(UserPreferencesUpdateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data

    class Meta:
        model = UserPreferences
        fields = ('send_emails',)
