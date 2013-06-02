'''
Created on Jun 1, 2013

@author: Horacio G. de Oro
'''

from django import forms

from lumina.models import Image


class ImageForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude = ('user',)
