"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os

from mock import Mock
from PIL import Image as PilImage
from StringIO import StringIO

from django.test import TestCase
from django.test.utils import override_settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from lumina.pil_utils import generate_thumbnail
from lumina.models import Image, Album


MEDIA_ROOT_FOR_TESTING = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], '../test/test-images')


#def get_test_image_path():
#    test_images_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0],
#        '../test/test-images')
#    image_path = os.path.join(test_images_dir, '8902217876_de6e699066.jpg')
#    return image_path


class PilUtilsTest(TestCase):

    # https://docs.djangoproject.com/en/1.5/topics/testing/overview/#overriding-settings
    # http://mock.readthedocs.org/en/latest/mock.html#mock.Mock
    @override_settings(MEDIA_ROOT=MEDIA_ROOT_FOR_TESTING)
    def test_generate_thumbnail(self):
        # Create mock
        image_mock = Mock(spec=Image)
        image_mock.image = Mock(spec=['path'])
        image_mock.image.path = '8902217876_de6e699066.jpg'
        # Generate thumb
        thumb = generate_thumbnail(image_mock)
        self.assertTrue(thumb is not None)

        # Assert thumb is an image
        thumb_img = PilImage.open(StringIO(thumb))
        self.assertTrue(thumb_img is not None)

        # Assert generation fails for non-existing path
        image_mock.image.path = 'xxxxxxxxxxxxxxx.jpg'
        with self.assertRaises(IOError):
            generate_thumbnail(image_mock)

        # Assert generation fails for non-image files
        image_mock.image.path = 'this-file-isnt-a-image.jpg'
        with self.assertRaises(IOError) as cm:
            generate_thumbnail(image_mock)
        self.assertEqual(cm.exception.args, ('cannot identify image file',))


ADMIN_ALBUM_UUID = "1d300055-7b06-498d-bb33-43e263c6c95e"
ADMIN_ALBUM_ID = 1
ADMIN_IMAGE_ID = 1

JUAN_ALBUM_UUID = "16436663-7ae0-4902-888d-e1c4da976c25"
JUAN_ALBUM_ID = 2
JUAN_IMAGE_ID = 2

PRIVATE_URLS = [
    reverse('album_list'),
    reverse('album_detail', args=[1]),
    reverse('album_detail', args=[2]),
    reverse('album_create'),
    reverse('album_update', args=[1]),
    reverse('album_update', args=[2]),
    # TODO: complete this list
]


class PermissoinsTests(TestCase):
    fixtures = ['tests/users.json', 'tests/albums.json', 'tests/images.json']

    def _login(self, username):
        self.assertTrue(self.client.login(username=username, password=username))

    def test_required_fixtures_admin(self):
        u_admin = User.objects.get(username='admin')
        self.assertEqual(Album.objects.get(pk=ADMIN_ALBUM_ID).user, u_admin)
        self.assertEqual(Image.objects.get(pk=ADMIN_IMAGE_ID).user, u_admin)

    def test_required_fixtures_juan(self):
        u_juan = User.objects.get(username='juan')
        self.assertEqual(Album.objects.get(pk=JUAN_ALBUM_ID).user, u_juan)
        self.assertEqual(Image.objects.get(pk=JUAN_IMAGE_ID).user, u_juan)

    def test_anonymous_access_to_privates_views(self):
        """
        Anonymous access to private views should return redirects to login page
        """

        response = self.client.get(reverse('home'))
        self.assertTemplateUsed(response, 'lumina/index.html')

        for url in PRIVATE_URLS:
            response = self.client.get(url)
            redirect_to = "http://testserver/accounts/login/?next={0}".format(url)
            self.assertRedirects(response, redirect_to)
            response = self.client.get(redirect_to)
            self.assertTemplateUsed(response, 'registration/login.html')

    @override_settings(MEDIA_ROOT=MEDIA_ROOT_FOR_TESTING)
    def test_only_users_albums_are_shown(self):
        self._login('admin')
        # Create album
        response = self.client.get(reverse('shared_album_create'))
        self.assertTemplateUsed(response, 'lumina/sharedalbum_create_form.html')
        self.assertContains(response, ADMIN_ALBUM_UUID)
        self.assertNotContains(response, JUAN_ALBUM_UUID)

        # Create image
        response = self.client.get(reverse('image_create'))
        self.assertTemplateUsed(response, 'lumina/image_create_form.html')
        self.assertContains(response, ADMIN_ALBUM_UUID)
        self.assertNotContains(response, JUAN_ALBUM_UUID)

        # Update image
        response = self.client.get(reverse('image_update', args=[ADMIN_IMAGE_ID]))
        self.assertTemplateUsed(response, 'lumina/image_update_form.html')
        self.assertContains(response, ADMIN_ALBUM_UUID)
        self.assertNotContains(response, JUAN_ALBUM_UUID)

    def test_shared_album(self):
        # TODO: implement this
        pass

    def test_private_album(self):
        """
        Login with 'admin' user, and assert he cant' access other's stuff
        """
        self._login('admin')

        # View list of albums
        response = self.client.get(reverse('album_list'))
        self.assertTemplateUsed(response, 'lumina/album_list.html')
        self.assertContains(response, ADMIN_ALBUM_UUID)
        self.assertNotContains(response, JUAN_ALBUM_UUID)

        # View it's own album
        response = self.client.get(reverse('album_detail', args=[ADMIN_ALBUM_ID]))
        self.assertTemplateUsed(response, 'lumina/album_detail.html')
        self.assertContains(response, ADMIN_ALBUM_UUID)
        self.assertNotContains(response, JUAN_ALBUM_UUID)

        # View other's album
        response = self.client.get(reverse('album_detail', args=[JUAN_ALBUM_ID]))
        self.assertTemplateNotUsed(response, 'lumina/album_detail.html')
        self.assertEqual(response.status_code, 404)

        # Modify my album / other's album
        response = self.client.get(reverse('album_update', args=[ADMIN_ALBUM_ID]))
        self.assertTemplateUsed(response, 'lumina/album_update_form.html')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('album_update', args=[JUAN_ALBUM_ID]))
        self.assertTemplateNotUsed(response, 'lumina/album_update_form.html')
        self.assertEqual(response.status_code, 404)

    def test_private_images(self):
        """
        Login with 'admin' user, and assert he cant' access other's images
        """
        self._login('admin')

        # Modify my image / other's image
        response = self.client.get(reverse('image_update', args=[ADMIN_IMAGE_ID]))
        self.assertTemplateUsed(response, 'lumina/image_update_form.html')
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse('image_update', args=[JUAN_IMAGE_ID]))
        self.assertTemplateNotUsed(response, 'lumina/image_update_form.html')
        self.assertEqual(response.status_code, 404)

    #    def test_private_customers(self):
    #        """
    #        Login with 'admin' user, and assert he cant' access other's customers
    #        """
    #        self._login('admin')
    #
    #        # Modify my image / other's image
    #        response = self.client.get(reverse('image_update', args=[ADMIN_IMAGE_ID]))
    #        self.assertTemplateUsed(response, 'lumina/image_update_form.html')
    #        self.assertEqual(response.status_code, 200)
    #        response = self.client.get(reverse('image_update', args=[JUAN_IMAGE_ID]))
    #        self.assertTemplateNotUsed(response, 'lumina/image_update_form.html')
    #        self.assertEqual(response.status_code, 404)


#===============================================================================
# Selenium
#===============================================================================

if os.environ.get("RUN_SELENIUM", '0') == '1':
    from lumina.tests_selenium import *  # @UnusedWildImport
