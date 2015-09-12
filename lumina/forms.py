# -*- coding: utf-8 -*-

"""
Created on Jun 1, 2013

@author: Horacio G. de Oro
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.urlresolvers import reverse_lazy

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout

from localflavor.ar.forms import ARCUITField

from lumina import models
from lumina.models import Session, LuminaUser, Customer, SharedSessionByEmail, \
    Image, ImageSelection, SessionQuote, SessionQuoteAlternative,\
    UserPreferences, SessionType


class GenericCreateUpdateModelForm(forms.ModelForm):

    FORM_TITLE = None
    SUBMIT_LABEL = None
    CANCEL_URL = None
    FIELDS = []

    def __init__(self, *args, **kwargs):
        assert self.FORM_TITLE is not None
        assert self.SUBMIT_LABEL is not None
        assert self.CANCEL_URL is not None
        assert self.FIELDS

        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            layout.Fieldset(
                self.FORM_TITLE,
                *self.FIELDS
            ),
            bootstrap.FormActions(
                layout.Submit('submit_button', self.SUBMIT_LABEL, css_id='form-submit-button'),
                layout.HTML("<a class='btn btn-primary' href='{}'>Cancelar</a>".format(self.CANCEL_URL)),
            ),
        )


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

    class Meta:
        model = SharedSessionByEmail
        fields = ('session', 'shared_with',)


# ===============================================================================
# ImageSelection
# ===============================================================================

class ImageSelectionCreateForm(forms.ModelForm):

    def clean_image_quantity(self):
        data = self.cleaned_data['image_quantity']
        if data <= 0:
            raise forms.ValidationError("La cantidad de imagenes debe ser mayor a 0")

        # Always return the cleaned data, whether you have changed it or not.
        return data

    class Meta:
        model = ImageSelection
        fields = ('session', 'image_quantity', 'preview_size')
        # exclude = ('user', 'status', 'selected_images')


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

class _GenericSessionForm(GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('session_list')
    FIELDS = ['name', 'session_type', 'photographer', 'customer', 'worked_hours']

    class Meta:
        model = models.Session
        fields = ('name', 'session_type', 'photographer', 'customer', 'worked_hours')


class SessionCreateForm(_GenericSessionForm):
    FORM_TITLE = 'Crear nueva sesión fotográfica'
    SUBMIT_LABEL = 'Crear'


class SessionUpdateForm(_GenericSessionForm):
    FORM_TITLE = 'Actualizar sesión fotográfica'
    SUBMIT_LABEL = 'Guardar'


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
            'fecha_creacion_desde',
            'fecha_creacion_hasta',
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
        self.fields['session_type'].queryset = SessionType.objects.session_type_of(photographer)

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

    class Meta:
        model = Image
        fields = ('image', 'session',)


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
            'fecha_creacion_desde',
            'fecha_creacion_hasta',
            'customer',
            'session_type',
            'page',
            bootstrap.FormActions(
                layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
            ),
        )
        self.fields['customer'].queryset = Customer.objects.customers_of(user)
        self.fields['session_type'].queryset = SessionType.objects.session_type_of(user)

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

class _GenericCustomerForm(GenericCreateUpdateModelForm):

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

class _GenericCustomerTypeForm(GenericCreateUpdateModelForm):

    CANCEL_URL = reverse_lazy('customer_type_list')
    FIELDS = ['name']

    class Meta:
        model = models.CustomerType
        fields = ('name',)


class CustomerTypeCreateForm(_GenericCustomerTypeForm):
    FORM_TITLE = 'Crear nuevo tipo de cliente'
    SUBMIT_LABEL = 'Crear'


class CustomerTypeUpdateForm(_GenericCustomerTypeForm):
    FORM_TITLE = 'Actualizar tipo de cliente'
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


# ===============================================================================
# User
# ===============================================================================

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(max_length=20, required=True,
                                widget=forms.PasswordInput(),
                                label='Contrasena')
    password2 = forms.CharField(max_length=20, required=True,
                                widget=forms.PasswordInput(),
                                label='Contrasena (otra vez)')

    class Meta:
        model = LuminaUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
            'phone', 'cellphone', 'alternative_email', 'notes'
        )

    def clean(self):
        super(UserCreateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data


class UserUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(), label='Contrasena',
        help_text="Ingrese la nueva contraseña (si desea cambiarla)")
    password2 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(),
        label='Contrasena (otra vez)',
        help_text="Repita la nueva contraseña (si desea cambiarla)")

    class Meta:
        model = LuminaUser
        fields = (
            'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
            'phone', 'cellphone', 'alternative_email', 'notes'
        )

    def clean(self):
        super(UserUpdateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data


# ===============================================================================
# SessionQuote
# ===============================================================================

class SessionQuoteCreateForm(forms.ModelForm):

    class Meta:
        model = SessionQuote
        fields = (
            'name', 'customer', 'image_quantity', 'stipulated_date', 'cost',
            'stipulated_down_payment', 'give_full_quality_images',
            'terms')


class SessionQuoteUpdateForm(forms.ModelForm):

    class Meta:
        model = SessionQuote
        fields = ('name', 'customer', 'image_quantity', 'cost',
                  'give_full_quality_images', 'terms')


class SessionQuoteUpdate2Form(forms.ModelForm):

    class Meta:
        model = SessionQuote
        fields = []


class SessionQuoteSearchForm(forms.Form):

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
                                        label='Archivados',
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
    page = forms.CharField(max_length=5, required=False, widget=forms.HiddenInput)

    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = 'quote_search'
        self.helper.form_id = 'form-session-quote-search'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        assert isinstance(user, LuminaUser)
        if user.is_photographer():
            self.helper.layout = helper.Layout(
                bootstrap.InlineRadios('archived_status'),
                'fecha_creacion_desde',
                'fecha_creacion_hasta',
                'customer',
                'page',
                bootstrap.FormActions(
                    layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
                ),
            )
            self.fields['customer'].queryset = Customer.objects.customers_of(user)
        else:
            self.helper.layout = helper.Layout(
                'fecha_creacion_desde',
                'fecha_creacion_hasta',
                'page',
                bootstrap.FormActions(
                    layout.Submit('submit_button', 'Buscar', css_id='form-submit-button'),
                ),
            )

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
# SessionQuoteAlternative
# ===============================================================================

class SessionQuoteAlternativeCreateForm(forms.ModelForm):

    class Meta:
        model = SessionQuoteAlternative
        fields = ('image_quantity', 'cost')

# # inline formset + class based views -> http://haineault.com/blog/155/
#
# # from django.forms.models import BaseModelFormSet
# # class BaseSessionQuoteAlternativeFormSet(BaseModelFormSet):
# #     def __init__(self, *args, **kwargs):
# #         super(BaseSessionQuoteAlternativeFormSet, self).__init__(*args, **kwargs)
# #         self.queryset = Author.objects.filter()
# #
# # SessionQuoteAlternativeFormSet = modelformset_factory(SessionQuoteAlternative,
# #                                                       formset=BaseSessionQuoteAlternativeFormSet)
#
# # SessionQuoteAlternativeFormSet = modelformset_factory(SessionQuoteAlternative)
#
# SessionQuoteAlternativeFormSet = inlineformset_factory(SessionQuote,
#                                                        SessionQuoteAlternative,
#                                                        can_delete=True,
#                                                        extra=3)
