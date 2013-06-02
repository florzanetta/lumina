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
import json

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

    @classmethod
    def setUpClass(cls):
        cls.selenium = _get_webdriver()
        super(LuminaSeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super(LuminaSeleniumTests, cls).tearDownClass()

    def _wait_until_render_done(self):
        """
        Wait until the browser finished rendering the HTML.
        To be used after clics, submits. etc.
        """
        # https://docs.djangoproject.com/en/1.5/topics/testing/overview/#django.test.LiveServerTestCase @IgnorePep8
        WebDriverWait(self.selenium, 5).until(
            lambda driver: driver.find_element_by_tag_name('body'))

    def _get_dump_of_objects(self):
        """
        Returns the objects dumped with a {% dump_objects %}
        """
        debug_dump_of_objects = self.selenium.execute_script(
            "return $('#debug_dump_of_objects').html();")
        self.assertTrue(debug_dump_of_objects,
            "There is no 'debug_dump_of_objects' element in the HTML."
            "Maybe you forgot to use '{% dump_objects %}'?")
        dumped_objects = {}
        try:
            level0_obj = json.loads(debug_dump_of_objects)
        except:
            print "-" * 70
            print debug_dump_of_objects
            print "-" * 70
            raise
        for key, value in level0_obj.iteritems():
            try:
                dumped_objects[key] = json.loads(value)
            except:
                dumped_objects[key] = value
        return dumped_objects

    def _assert_user_in_dump_of_objects(self, dump_of_objects, username, key='user'):
        """
        Asserts that dump of objects has a reference to user equals to `username`.
        To assert that user is AnonymousUser, use `username=None`.

        Examples:
        _assert_user_in_dump_of_objects(objs, None) -> Assert anonymous
        _assert_user_in_dump_of_objects(objs, 'admin') -> Assert default 'admin'
        _assert_user_in_dump_of_objects(objs, 'admin', key='logged_in_user')
        """
        self.assertIn(key, dump_of_objects,
            "Dump of objects doesn't contains 'user' key.")
        user = dump_of_objects[key]
        if username is None:
            self.assertEqual(user, 'AnonymousUser')
        else:
            self.assertNotEqual(user, 'AnonymousUser',
                "Dump of objects has reference to 'AnonymousUser'")
            try:
                self.assertEqual(user[0]['fields']['username'], username)
            except:
                print dump_of_objects
                raise

    def _go_home(self):
        """Goes to the home page and return _get_dump_of_objects()"""
        self.selenium.get('%s%s' % (self.live_server_url, '/'))
        self._wait_until_render_done()
        objs = self._get_dump_of_objects()
        return objs

    def _logout(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/logout/'))
        self._wait_until_render_done()
        objs = self._get_dump_of_objects()
        return objs

    def _assert_login_form_was_displayed(self):
        objs = self._get_dump_of_objects()
        self.assertEqual(objs, {})
        self.assertTrue(self.selenium.find_element_by_id('submit_button'))
        self.assertTrue(self.selenium.find_element_by_id("id_username"))
        self.assertTrue(self.selenium.find_element_by_id("id_password"))

    def test_login(self):
        # Go home
        objs = self._go_home()
        self._assert_user_in_dump_of_objects(objs, None)
        # Go to album list
        self.selenium.get('%s%s' % (self.live_server_url, '/album/list/'))
        self._wait_until_render_done()
        self._assert_login_form_was_displayed()
        # Do login
        self.selenium.find_element_by_id("id_username").send_keys('admin')
        self.selenium.find_element_by_id("id_password").send_keys('admin')
        self.selenium.find_element_by_id('submit_button').click()
        self._wait_until_render_done()
        # Check login went well
        objs = self._get_dump_of_objects()
        self._assert_user_in_dump_of_objects(objs, 'admin')
        # Get list of albums
        objs = self._get_dump_of_objects()
        self.assertEqual(objs['object_list'], [])
        # Logout and check
        self.selenium.get('%s%s' % (self.live_server_url, '/accounts/logout/'))
        self._wait_until_render_done()
        objs = self._get_dump_of_objects()
        self._assert_user_in_dump_of_objects(objs, None)
