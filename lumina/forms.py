'''
Created on Jun 1, 2013

@author: Horacio G. de Oro
'''

from django import forms

from lumina.models import Image, Album, SharedAlbum


#===============================================================================
# SharedAlbum
#===============================================================================

class SharedAlbumCreateForm(forms.ModelForm):

    class Meta:
        model = SharedAlbum
        exclude = ('user', 'random_hash',)


#===============================================================================
# Album
#===============================================================================

class AlbumCreateForm(forms.ModelForm):

    class Meta:
        model = Album
        exclude = ('user',)

AlbumUpdateForm = AlbumCreateForm


#===============================================================================
# Image
#===============================================================================

class ImageCreateForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude = ('user', 'size', 'original_filename', 'content_type',)


class ImageUpdateForm(forms.ModelForm):

    class Meta:
        model = Image
        exclude = ('user', 'image', 'size', 'original_filename', 'content_type',)
