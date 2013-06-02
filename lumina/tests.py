"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import os
import unittest
import subprocess

from mock import Mock
from PIL import  Image as PilImage
from StringIO import StringIO

from selenium.webdriver.support.wait import WebDriverWait

from django.test import TestCase
from django.test.utils import override_settings
from django.test import LiveServerTestCase
from django.conf import settings

from lumina.pil_utils import generate_thumbnail
from lumina.models import Image

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


# https://docs.djangoproject.com/en/1.5/topics/testing/overview/#django.test.LiveServerTestCase

def _get_webdriver():
    # First, try Chrome
    chromedriver_bin = None
    try:
        chromedriver_bin = subprocess.check_output(["which", "chromedriver"],
            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError:
        for an_executable in settings.SELENIUM_WEBDRIVER_BIN:
            if os.path.exists(an_executable):
                chromedriver_bin = an_executable
                break
    if chromedriver_bin is not None:
        from selenium.webdriver.chrome.webdriver import WebDriver as ChromeWebDriver
        return ChromeWebDriver(executable_path=chromedriver_bin)
    else:
        from selenium.webdriver.firefox.webdriver import WebDriver as FirefoxWebDriver
        return FirefoxWebDriver()


@unittest.skipUnless(os.environ.get("RUN_SELENIUM", '0') == '1', "RUN_SELENIUM != 1")
class LuminaSeleniumTests(LiveServerTestCase):
    fixtures = ['admin_user.json']

    def _wait_until_render_done(self):
        # https://docs.djangoproject.com/en/1.5/topics/testing/overview/#django.test.LiveServerTestCase @IgnorePep8
        WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element_by_tag_name('body'))

    @classmethod
    def setUpClass(cls):
        cls.selenium = _get_webdriver()
        super(LuminaSeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LuminaSeleniumTests, cls).tearDownClass()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/album/list/'))
        self._wait_until_render_done()
        username_input = self.selenium.find_element_by_id("id_username")
        username_input.send_keys('admin')
        password_input = self.selenium.find_element_by_id("id_password")
        password_input.send_keys('admin')
        self.selenium.find_element_by_id('submit_button').click()
        self._wait_until_render_done()
