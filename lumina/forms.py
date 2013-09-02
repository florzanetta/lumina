'''
Created on Jun 1, 2013

@author: Horacio G. de Oro
'''

from django import forms
from django.forms.widgets import CheckboxSelectMultiple

from lumina.models import Session, LuminaUser, Customer, SharedSessionByEmail


#===============================================================================
# SharedSessionByEmail (ex: SharedAlbum)
#===============================================================================

class SharedSessionByEmailCreateForm(forms.ModelForm):

    class Meta:
        model = SharedSessionByEmail
        fields = ('session', 'shared_with',)


#===============================================================================
# ImageSelection
#===============================================================================

# class ImageSelectionCreateForm(forms.ModelForm):
#
#     def clean_image_quantity(self):
#         data = self.cleaned_data['image_quantity']
#         if data <= 0:
#             raise(forms.ValidationError("La cantidad de imagenes debe ser mayor a 0"))
#
#         # Always return the cleaned data, whether you have changed it or not.
#         return data
#
#     class Meta:
#         model = ImageSelection
#         exclude = ('user', 'status', 'selected_images')


#===============================================================================
# Session
#===============================================================================

class SessionCreateForm(forms.ModelForm):

    class Meta:
        model = Session
        exclude = ('studio', )


class SessionUpdateForm(forms.ModelForm):

    class Meta:
        model = Session
        exclude = ('studio',)
        widgets = {
            'shared_with': CheckboxSelectMultiple(),
        }


#===============================================================================
# Image
#===============================================================================

# class ImageCreateForm(forms.ModelForm):
#
#     class Meta:
#         model = Image
#         exclude = ('user', 'size', 'original_filename', 'content_type',)
#
#
# class ImageUpdateForm(forms.ModelForm):
#
#     class Meta:
#         model = Image
#         exclude = ('user', 'image', 'size', 'original_filename', 'content_type',)


#===============================================================================
# Customer
#===============================================================================

class CustomerCreateForm(forms.ModelForm):

    class Meta:
        model = Customer
        fields = (
            'name', 'address', 'phone',
        )

CustomerUpdateForm = CustomerCreateForm


#===============================================================================
# User
#===============================================================================

class UserCreateForm(forms.ModelForm):
    password1 = forms.CharField(
        max_length=20, required=True, widget=forms.PasswordInput(), label=u'Contrasena')
    password2 = forms.CharField(
      max_length=20, required=True, widget=forms.PasswordInput(), label=u'Contrasena (otra vez)')

    class Meta:
        model = LuminaUser
        fields = (
            'username', 'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2'
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
        max_length=20, required=False, widget=forms.PasswordInput(), label=u'Contrasena')
    password2 = forms.CharField(
        max_length=20, required=False, widget=forms.PasswordInput(),
        label=u'Contrasena (otra vez)')

    class Meta:
        model = LuminaUser
        fields = (
            'first_name', 'last_name', 'email', 'is_active', 'password1', 'password2'
        )

    def clean(self):
        super(UserUpdateForm, self).clean()
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError('Los passwords no concuerdan')
        return self.cleaned_data
