# -*- coding: utf-8 -*-

from django import forms
from django.core.urlresolvers import reverse_lazy

from lumina import forms_utils
from lumina.models import LuminaUser


class _GenericUserCreateUpdateForm(forms_utils.GenericCreateUpdateModelForm):
    """Generic for for any kind of user.

    Has passwords and validation for passwords.
    """

    PASSWORD_REQUIRED = None  # `True` or `False` (fails if not overwritting)
    HELP_TEXT_FOR_PASSWORD = None  # `str`, or 'None'

    #
    # `required` and `help_text` are overwritting in __init__(), since the value of
    # PASSWORD_REQUIRED & HELP_TEXT_FOR_PASSWORD when the property is defined is
    # the value in THIS class, NOT the child class
    #

    password1 = forms.CharField(max_length=20,
                                required='',  # will be overwritten by __init__()
                                help_text='',  # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label='Contrasena')

    password2 = forms.CharField(max_length=20,
                                required='',  # will be overwritten by __init__()
                                help_text='',  # will be overwritten by __init__()
                                widget=forms.PasswordInput(),
                                label='Contrasena (otra vez)')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.PASSWORD_REQUIRED is True or self.PASSWORD_REQUIRED is False
        self.fields['password1'].required = self.PASSWORD_REQUIRED
        self.fields['password2'].required = self.PASSWORD_REQUIRED

        if self.HELP_TEXT_FOR_PASSWORD:
            self.fields['password1'].help_text = self.HELP_TEXT_FOR_PASSWORD
            self.fields['password2'].help_text = self.HELP_TEXT_FOR_PASSWORD

    def clean(self):
        super().clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data


# ===============================================================================
# For CUSTOMERs
# ===============================================================================

class CustomerUserCreateForm(_GenericUserCreateUpdateForm):

    # ----- <GenericCreateUpdateModelForm> -----

    FORM_TITLE = 'Crear usuario para cliente'
    SUBMIT_LABEL = 'Crear'
    FIELDS = [
        'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
        'phone', 'cellphone', 'alternative_email', 'notes'
    ]

    def get_cancel_url(self):
        return reverse_lazy('customer_user_list', args=[self.customer_id])

    # ----- </GenericCreateUpdateModelForm> -----

    PASSWORD_REQUIRED = True

    def __init__(self, *args, **kwargs):
        self.customer_id = kwargs.pop('customer_id')
        super().__init__(*args, **kwargs)

    class Meta:
        model = LuminaUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
            'phone', 'cellphone', 'alternative_email', 'notes'
        )


class CustomerUserUpdateForm(_GenericUserCreateUpdateForm):

    # ----- <GenericCreateUpdateModelForm> -----

    FORM_TITLE = 'Actualizar usuario de cliente'
    SUBMIT_LABEL = 'Guardar'
    FIELDS = [
        'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
        'phone', 'cellphone', 'alternative_email', 'notes'
    ]

    def get_cancel_url(self):
        return reverse_lazy('customer_user_list', args=[self.instance.user_for_customer.id])

    # ----- </GenericCreateUpdateModelForm> -----

    PASSWORD_REQUIRED = False
    HELP_TEXT_FOR_PASSWORD = "Ingrese la nueva contraseña (sólo si desea cambiarla)"

    class Meta:
        model = LuminaUser
        fields = (
            'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
            'phone', 'cellphone', 'alternative_email', 'notes'
        )


# ===============================================================================
# For STUDIOs (photographers)
# ===============================================================================

class SetudioUserCreateForm(_GenericUserCreateUpdateForm):

    # ----- <GenericCreateUpdateModelForm> -----
    FORM_TITLE = 'Crear usuario para fotógrafo'
    SUBMIT_LABEL = 'Crear'
    CANCEL_URL = reverse_lazy('studio_user_list')
    FIELDS = [
        'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
    ]

    # ----- </GenericCreateUpdateModelForm> -----

    PASSWORD_REQUIRED = True

    class Meta:
        model = LuminaUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2',
        )
