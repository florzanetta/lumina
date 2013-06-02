'''
Created on Jun 1, 2013

@author: Horacio G. de Oro
'''

from django import forms

from lumina.models import Image


class ImageCreateForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude = ('user',)


class ImageUpdateForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude = ('user', 'image')
