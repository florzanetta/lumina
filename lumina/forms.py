# -*- coding: utf-8 -*-

"""
Created on Jun 1, 2013

@author: Horacio G. de Oro
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from crispy_forms import bootstrap
from crispy_forms import helper
from crispy_forms import layout

from localflavor.ar.forms import ARCUITField

from lumina.models import Session, LuminaUser, Customer, SharedSessionByEmail, \
    Image, ImageSelection, SessionQuote, SessionQuoteAlternative,\
    UserPreferences, SessionType


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

class SessionCreateForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = ('name', 'session_type', 'photographer', 'customer', )  # 'shared_with',


class SessionUpdateForm(forms.ModelForm):

    class Meta:
        model = Session
        fields = ('name', 'session_type', 'photographer', 'customer', 'worked_hours', )  # 'shared_with',
        # widgets = {
        #    'shared_with': CheckboxSelectMultiple(),
        # }


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
    customer = forms.ModelChoiceField(Session.objects.none(),
                                      empty_label='Todos los clientes',
                                      label='Cliente',
                                      required=False)
    session_type = forms.ModelChoiceField(SessionType.objects.none(),
                                          empty_label='Todos los tipos de sesiones',
                                          label='Tipo de sesión',
                                          required=False)

    def __init__(self, photographer=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = helper.FormHelper()
        self.helper.form_action = 'session_search'

        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'

        self.helper.layout = helper.Layout(
            bootstrap.InlineRadios('archived_status'),
            'fecha_creacion_desde',
            'fecha_creacion_hasta',
            'customer',
            'session_type',
            bootstrap.FormActions(
                layout.Submit('submit', 'Buscar'),
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


# ===============================================================================
# Customer
# ===============================================================================

class CustomerCreateForm(forms.ModelForm):

    cuit = ARCUITField(max_length=13, min_length=0, required=False,
                       help_text="Formato: XX-XXXXXXXX-X")

    class Meta:
        model = Customer
        fields = (
            'name', 'customer_type', 'address', 'phone', 'city', 'iva', 'cuit',
            'ingresos_brutos', 'notes'
        )

CustomerUpdateForm = CustomerCreateForm


# ===============================================================================
# UserPreferences
# ===============================================================================

class UserPreferencesUpdateForm(forms.ModelForm):
    password1 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(), label='Contrasena',
        help_text="Ingrese la nueva contraseña (si desea cambiarla)")
    password2 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(),
        label='Contrasena (otra vez)',
        help_text="Repita la nueva contraseña (si desea cambiarla)")

    def clean(self):
        super(UserPreferencesUpdateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data

    class Meta:
        model = UserPreferences
        fields = ('send_emails', 'password1', 'password2',)


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
