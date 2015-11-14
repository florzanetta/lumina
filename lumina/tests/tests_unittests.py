# -*- coding: utf-8 -*-

import decimal
import os

# from mock import Mock
# from PIL import Image as PilImage
# from io import StringIO

from django.test import TestCase
# from django.test.utils import override_settings
# from django.core.urlresolvers import reverse
# from django.contrib.auth import authenticate
from django.utils import timezone

from lumina.models import SessionQuote, Studio, LuminaUser, \
    SessionQuoteAlternative
# from lumina.forms import SessionQuoteAlternativeFormSet
# from lumina.pil_utils import generate_thumbnail
from lumina.utils import year_month_iterator

MEDIA_ROOT_FOR_TESTING = os.path.join(os.path.split(
    os.path.abspath(__file__))[0], 'test-images')


# def get_test_image_path():
#    test_images_dir = os.path.join(os.path.split(os.path.abspath(__file__))[0],
#        'test-images')
#    image_path = os.path.join(test_images_dir, '8902217876_de6e699066.jpg')
#    return image_path

# FIXME: REFACTOR: refactor this tests
# class LuminaTestCase(TestCase):
#
#     def _login(self, username, password=None):
#         self.assertTrue(self.client.login(username=username, password=password or username))
#         self._logged_in_user = LuminaUser.objects.get(username=username)
#
#     def login_admin(self):
#         """Logon with the 'admin' user (photographer)"""
#         self._login('admin')
#
#     def login_juan(self):
#         """Logon with the 'juan' user (photographer)"""
#         self._login('juan')
#
#     def login_albert(self):
#         """Logon with the 'albert' user (customer)"""
#         self._login('customer-ba07eb50-9fb5-4593-98', 'albert')
#
#     def login_max(self):
#         """Logon with the 'max' user (customer)"""
#         self._login('customer-957a6230-3eac-4ee1-a4', 'max')

# FIXME: REFACTOR: refactor this tests
# class PilUtilsTest(TestCase):
#
#     # https://docs.djangoproject.com/en/1.5/topics/testing/overview/#overriding-settings
#     # http://mock.readthedocs.org/en/latest/mock.html#mock.Mock
#     @override_settings(MEDIA_ROOT=MEDIA_ROOT_FOR_TESTING)
#     def test_generate_thumbnail(self):
#         # Create mock
#         image_mock = Mock(spec=Image)
#         image_mock.image = Mock(spec=['path'])
#         image_mock.image.path = '8902217876_de6e699066.jpg'
#         # Generate thumb
#         thumb = generate_thumbnail(image_mock)
#         self.assertTrue(thumb is not None)
#
#         # Assert thumb is an image
#         thumb_img = PilImage.open(StringIO(thumb))
#         self.assertTrue(thumb_img is not None)
#
#         # Assert generation fails for non-existing path
#         image_mock.image.path = 'xxxxxxxxxxxxxxx.jpg'
#         with self.assertRaises(IOError):
#             generate_thumbnail(image_mock)
#
#         # Assert generation fails for non-image files
#         image_mock.image.path = 'this-file-isnt-a-image.jpg'
#         with self.assertRaises(IOError) as cm:
#             generate_thumbnail(image_mock)
#         self.assertEqual(cm.exception.args, ('cannot identify image file',))

# FIXME: REFACTOR: refactor this tests
# ADMIN_ALBUM_UUID = "1d300055-7b06-498d-bb33-43e263c6c95e"
# ADMIN_ALBUM_ID = 1
# ADMIN_IMAGE_ID = 1
# ADMIN_CUSTOMER_UUID = "ba07eb50-9fb5-4593-98"
# ADMIN_CUSTOMER_ID = 3
#
# JUAN_ALBUM_UUID = "16436663-7ae0-4902-888d-e1c4da976c25"
# JUAN_ALBUM_ID = 2
# JUAN_IMAGE_ID = 2
# JUAN_CUSTOMER_UUID = "957a6230-3eac-4ee1-a4"
# JUAN_CUSTOMER_ID = 4
#
# PRIVATE_URLS = [
#     reverse('album_list'),
#     reverse('session_detail', args=[1]),
#     reverse('session_detail', args=[2]),
#     reverse('session_create'),
#     reverse('album_update', args=[1]),
#     reverse('album_update', args=[2]),
#     # TODO: complete this list
# ]


# FIXME: REFACTOR: refactor this tests
# class BasicAccessTest(LuminaTestCase):
#     fixtures = ['tests/users.json', 'tests/albums.json', 'tests/images.json']
#
#     def test_access_to_pages(self):
#         for login_func in (self.login_admin, self.login_juan, self.login_albert, self.login_max):
#             login_func()  # user -> self._logged_in_user
#             if self._logged_in_user.user_type == LuminaUser.PHOTOGRAPHER:
#                 for view_name in (
#                     'home', 'album_list', 'session_create', 'shared_session_by_email_create',
#                         'image_list', 'image_create', 'customer_list', 'customer_create'):
#                     response = self.client.get(reverse(view_name))
#                     self.assertEqual(response.status_code, 200)
#             else:
#                 # TODO: do tests for customer
#                 pass
#
#             all_the_images = []
#             for album in Album.objects.all_visible(self._logged_in_user):
#                 # Views to test: "session_detail", "album_update"
#                 self.assertEqual(self.client.get(
#                     reverse("session_detail", args=[album.id])).status_code, 200)
#                 all_the_images += list(album.image_set.all())
#
#                 # If the user is the album's owner, the user must be able to update it
#                 if album.user.pk == self._logged_in_user.pk:
#                     self.assertEqual(self._logged_in_user.user_type, LuminaUser.PHOTOGRAPHER,
#                                      "The user {0} owns an album, but it's a customer, "
#                                      "not a photographer!".format(self._logged_in_user))
#                     response = self.client.get(reverse("album_update", args=[album.id]))
#                     self.assertEqual(
#                         response.status_code, 200,
#                         msg="Status code != 200 - User: {0} - Album: {1}"
#                             "".format(self._logged_in_user, album.id))
#
#             # View to test: "image_update"
#             all_the_images = set(
#                 all_the_images + list(Image.objects.all_my_images(self._logged_in_user)))
#             for image in all_the_images:
#                 if image.user == self._logged_in_user:
#                     self.assertEqual(self.client.get(
#                         reverse("image_update", args=[image.id])).status_code, 200)
#                 self.assertEqual(self.client.get(
#                     reverse("image_thumb", args=[image.id])).status_code, 200)
#                 self.assertEqual(self.client.get(
#                     reverse("image_thumb_64x64", args=[image.id])).status_code, 200)
#                 self.assertEqual(self.client.get(
#                     reverse("image_download", args=[image.id])).status_code, 200)
#
#             if self._logged_in_user.user_type == LuminaUser.PHOTOGRAPHER:
#                 for customer in self._logged_in_user.all_my_customers():
#                     self.assertEqual(self.client.get(
#                         reverse("customer_update", args=[customer.id])).status_code, 200)
#             else:
#                 # TODO: do tests for customer
#                 pass


# FIXME: REFACTOR: refactor this tests
# class PermissoinsTests(LuminaTestCase):
#     fixtures = ['tests/users.json', 'tests/albums.json', 'tests/images.json']
#
#     def test_required_fixtures_admin(self):
#         u_admin = LuminaUser.objects.get(username='admin')
#         self.assertEqual(Album.objects.get(pk=ADMIN_ALBUM_ID).user, u_admin)
#         self.assertEqual(Image.objects.get(pk=ADMIN_IMAGE_ID).user, u_admin)
#
#     def test_required_fixtures_juan(self):
#         u_juan = LuminaUser.objects.get(username='juan')
#         self.assertEqual(Album.objects.get(pk=JUAN_ALBUM_ID).user, u_juan)
#         self.assertEqual(Image.objects.get(pk=JUAN_IMAGE_ID).user, u_juan)
#
#     def test_anonymous_access_to_privates_views(self):
#         """
#         Anonymous access to private views should return redirects to login page
#         """
#
#         response = self.client.get(reverse('home'))
#         self.assertTemplateUsed(response, 'lumina/index.html')
#
#         for url in PRIVATE_URLS:
#             response = self.client.get(url)
#             redirect_to = "http://testserver/accounts/login/?next={0}".format(url)
#             self.assertRedirects(response, redirect_to)
#             response = self.client.get(redirect_to)
#             self.assertTemplateUsed(response, 'registration/login.html')
#
#     @override_settings(MEDIA_ROOT=MEDIA_ROOT_FOR_TESTING)
#     def test_only_users_albums_are_shown(self):
#         self._login('admin')
#         # Create album
#         response = self.client.get(reverse('shared_session_by_email_create'))
#         self.assertTemplateUsed(response, 'lumina/sharedalbum_create_form.html')
#         self.assertContains(response, ADMIN_ALBUM_UUID)
#         self.assertNotContains(response, JUAN_ALBUM_UUID)
#
#         # Create image
#         response = self.client.get(reverse('image_create'))
#         self.assertTemplateUsed(response, 'lumina/image_create_form.html')
#         self.assertContains(response, ADMIN_ALBUM_UUID)
#         self.assertNotContains(response, JUAN_ALBUM_UUID)
#
#         # Update image
#         response = self.client.get(reverse('image_update', args=[ADMIN_IMAGE_ID]))
#         self.assertTemplateUsed(response, 'lumina/image_update_form.html')
#         self.assertContains(response, ADMIN_ALBUM_UUID)
#         self.assertNotContains(response, JUAN_ALBUM_UUID)
#
#     def test_shared_album(self):
#         # TODO: implement this
#         pass
#
#     def test_private_album(self):
#         """
#         Login with 'admin' user, and assert he cant' access other's stuff
#         """
#         self._login('admin')
#
#         # View list of albums
#         response = self.client.get(reverse('album_list'))
#         self.assertTemplateUsed(response, 'lumina/album_list.html')
#         self.assertContains(response, ADMIN_ALBUM_UUID)
#         self.assertNotContains(response, JUAN_ALBUM_UUID)
#
#         # View it's own album
#         response = self.client.get(reverse('session_detail', args=[ADMIN_ALBUM_ID]))
#         self.assertTemplateUsed(response, 'lumina/session_detail.html')
#         self.assertContains(response, ADMIN_ALBUM_UUID)
#         self.assertNotContains(response, JUAN_ALBUM_UUID)
#
#         # View other's album
#         response = self.client.get(reverse('session_detail', args=[JUAN_ALBUM_ID]))
#         self.assertTemplateNotUsed(response, 'lumina/session_detail.html')
#         self.assertEqual(response.status_code, 404)
#
#         # Modify my album / other's album
#         response = self.client.get(reverse('album_update', args=[ADMIN_ALBUM_ID]))
#         self.assertTemplateUsed(response, 'lumina/album_update_form.html')
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse('album_update', args=[JUAN_ALBUM_ID]))
#         self.assertTemplateNotUsed(response, 'lumina/album_update_form.html')
#         self.assertEqual(response.status_code, 404)
#
#     def test_private_images(self):
#         """
#         Login with 'admin' user, and assert he cant' access other's images
#         """
#         self._login('admin')
#
#         # Modify my image / other's image
#         response = self.client.get(reverse('image_update', args=[ADMIN_IMAGE_ID]))
#         self.assertTemplateUsed(response, 'lumina/image_update_form.html')
#         self.assertEqual(response.status_code, 200)
#         response = self.client.get(reverse('image_update', args=[JUAN_IMAGE_ID]))
#         self.assertTemplateNotUsed(response, 'lumina/image_update_form.html')
#         self.assertEqual(response.status_code, 404)
#
#     def test_private_customers(self):
#         """
#         Login with 'admin' user, and assert he cant' access other's customers
#         """
#         self._login('admin')
#
#         # List admin's customers
#         response = self.client.get(reverse('customer_list'))
#         self.assertTemplateUsed(response, 'lumina/customer_list.html')
#         self.assertContains(response, ADMIN_CUSTOMER_UUID)
#         self.assertNotContains(response, JUAN_CUSTOMER_UUID)
#
#         # Modify my customer / other's image
#         response = self.client.get(reverse('customer_update', args=[ADMIN_CUSTOMER_ID]))
#         self.assertTemplateUsed(response, 'lumina/customer_update_form.html')
#         self.assertEqual(response.status_code, 200)
#
#         response = self.client.get(reverse('customer_update', args=[JUAN_CUSTOMER_ID]))
#         self.assertTemplateNotUsed(response, 'lumina/customer_update_form.html')
#         self.assertEqual(response.status_code, 404)


# FIXME: REFACTOR: refactor this tests
# class CustomerTests(LuminaTestCase):
#     fixtures = ['tests/users.json']
#
#     def test_hashed_password(self):
#         self.login_admin()
#
#         response = self.client.get(reverse('customer_create'))
#         self.assertTemplateUsed(response, 'lumina/customer_create_form.html')
#         self.assertEqual(response.status_code, 200)
#
#         self.assertEqual(LuminaUser.objects.filter(username='erwin').count(), 0)
#
#         form_data = {
#             'username': 'erwin',
#             'first_name': 'Erwin',
#             'last_name': u'Schrödinger',
#             'email': 'erwin@example.com',
#             'password1': 'erwin123',
#             'password2': 'erwin123',
#         }
#         response = self.client.post(reverse('customer_create'), form_data)
#         self.assertEqual(LuminaUser.objects.filter(username='erwin').count(), 1)
#
#         self.assertEqual(
#             LuminaUser.objects.filter(username='erwin', password='erwin123').count(), 0,
#             msg="The password was saved in the database as clear-text!!!")
#
#         self.assertTrue(
#             authenticate(username='erwin', password='erwin123'),
#             msg="Couldn't authenticate the created user")


# FIXME: REFACTOR: refactor this tests
# class AlbumManagerTests(LuminaTestCase):
#     fixtures = ['tests/users.json', 'tests/albums.json', 'tests/images.json']
#
#     def setUp(self):
#         self.admin = LuminaUser.objects.get(username='admin')
#         self.juan = LuminaUser.objects.get(username='juan')
#         self.albert = LuminaUser.objects.get(username='customer-ba07eb50-9fb5-4593-98')
#         self.max = LuminaUser.objects.get(username='customer-957a6230-3eac-4ee1-a4')
#
#     def test_all_my_albums(self):
#         admin_albums = Album.objects.all_my_albums(self.admin)
#         self.assertEqual(admin_albums.count(), 1)
#         self.assertEqual(admin_albums.all()[0].id, 1)
#
#         juan_albums = Album.objects.all_my_albums(self.juan)
#         self.assertEqual(juan_albums.count(), 1)
#         self.assertEqual(juan_albums.all()[0].id, 2)
#
#         self.assertEqual(Album.objects.all_my_albums(self.albert).count(), 0)
#         self.assertEqual(Album.objects.all_my_albums(self.max).count(), 0)
#
#     def test_shared_with_me(self):
#         self.assertEqual(Album.objects.shared_with_me(self.admin).count(), 0)
#         self.assertEqual(Album.objects.shared_with_me(self.juan).count(), 0)
#         self.assertEqual(Album.objects.shared_with_me(self.albert).count(), 0)
#         self.assertEqual(Album.objects.shared_with_me(self.max).count(), 1)
#         album = Album.objects.shared_with_me(self.max).get()
#         self.assertEqual(album.user, self.juan)
#
#     def test_all_visible(self):
#         self.assertEqual(Album.objects.all_visible(self.admin).count(), 1)
#         self.assertEqual(Album.objects.all_visible(self.juan).count(), 1)
#         self.assertEqual(Album.objects.all_visible(self.albert).count(), 0)
#         self.assertEqual(Album.objects.all_visible(self.max).count(), 1)

class SessionQuoteModelTests(TestCase):
    fixtures = ['sample/studios.json', 'sample/customers.json',
                'sample/users.json']

    def setUp(self):
        self.studio = Studio.objects.get(pk=3)
        self.photographer = LuminaUser.objects.get_by_natural_key('fotografo1')
        self.user_for_customer = LuminaUser.objects.get_by_natural_key('cliente1')

        self.other_photographer = LuminaUser.objects.get_by_natural_key('juan')
        self.user_for_other_customer = LuminaUser.objects.get_by_natural_key('cliente2')

    def _create_quote(self):
        quote = SessionQuote.objects.create(studio=self.studio,
                                            customer=self.user_for_customer.user_for_customer,
                                            image_quantity=10,
                                            cost=12.34,
                                            stipulated_date=timezone.now(),
                                            stipulated_down_payment=0.0)
        return quote

    def _create_quote_alternatives(self, quote):
        return (
            SessionQuoteAlternative.objects.create(session_quote=quote,
                                                   image_quantity=10,
                                                   cost=decimal.Decimal('110.11')),
            SessionQuoteAlternative.objects.create(session_quote=quote,
                                                   image_quantity=20,
                                                   cost=decimal.Decimal('220.22'))
        )

    def test_cancel(self):
        count = SessionQuote.objects.all().count()
        q = self._create_quote()
        self.assertEqual(SessionQuote.objects.all().count(), count + 1)
        quote = SessionQuote.objects.get(pk=q.id)

        # Check that doesn't work for invalid users
        for invalid_user in (self.other_photographer,
                             self.user_for_other_customer,
                             self.user_for_customer):
            self.assertRaises(AssertionError, quote.cancel, invalid_user)

        quote.cancel(self.photographer)
        SessionQuote.objects.get(pk=q.id,
                                 status=SessionQuote.STATUS_CANCELED)

        # Assert no more state transitions are allowed
        self.assertRaises(AssertionError, quote.confirm, self.photographer)
        self.assertRaises(AssertionError, quote.cancel, self.photographer)
        self.assertRaises(AssertionError, quote.accept, self.user_for_customer, 0)
        self.assertRaises(AssertionError, quote.reject, self.user_for_customer)

    def test_confirm(self):
        count = SessionQuote.objects.all().count()
        q = self._create_quote()
        self.assertEqual(SessionQuote.objects.all().count(), count + 1)
        quote = SessionQuote.objects.get(pk=q.id)

        # Check that doesn't work for invalid users
        for invalid_user in (self.other_photographer,
                             self.user_for_other_customer,
                             self.user_for_customer):
            self.assertRaises(AssertionError, quote.confirm, invalid_user)

        # confirm()
        quote.confirm(self.photographer)
        SessionQuote.objects.get(pk=q.id,
                                 status=SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)

        # ----- cancel() -----

        # Check that cancel() doesn't work for invalid users
        for invalid_user in (self.other_photographer,
                             self.user_for_other_customer,
                             self.user_for_customer):
            self.assertRaises(AssertionError, quote.cancel, invalid_user)

    def test_accept_reject(self):
        count = SessionQuote.objects.all().count()

        q_accept = self._create_quote()
        self._create_quote_alternatives(q_accept)
        q_reject = self._create_quote()
        self._create_quote_alternatives(q_reject)

        self.assertEqual(SessionQuote.objects.all().count(), count + 2)
        q_accept = SessionQuote.objects.all().get(pk=q_accept.id)
        q_reject = SessionQuote.objects.all().get(pk=q_reject.id)

        self.assertEqual(q_accept.quote_alternatives.count(), 2)
        self.assertEqual(q_reject.quote_alternatives.count(), 2)

        self.assertEqual(len(SessionQuote.objects.get_waiting_for_customer_response(
            self.user_for_customer)), 0)

        # accept()/reject() should fail befor confirm()
        self.assertRaises(AssertionError, q_accept.accept, self.user_for_customer, None)
        self.assertRaises(AssertionError, q_reject.reject, self.user_for_customer)

        # confirm() the quotes
        q_accept.confirm(self.photographer)
        q_reject.confirm(self.photographer)

        self.assertEqual(len(SessionQuote.objects.get_waiting_for_customer_response(
            self.user_for_customer)), 2)

        # Check that doesn't work for invalid users
        for invalid_user in (self.other_photographer,
                             self.user_for_other_customer,
                             self.photographer):
            try:
                q_accept.accept(invalid_user, None)
                raise Exception("accept() didn't failed with uesr {}".format(invalid_user))
            except AssertionError:
                pass

            try:
                q_reject.reject(invalid_user)
                raise Exception("reject() didn't failed with uesr {}".format(invalid_user))
            except AssertionError:
                pass

        self.assertTrue(q_accept.accepted_rejected_by is None)
        self.assertTrue(q_accept.accepted_rejected_at is None)
        self.assertTrue(q_reject.accepted_rejected_by is None)
        self.assertTrue(q_reject.accepted_rejected_at is None)

        # accept() should sucess after confirm()
        q_accept.accept(self.user_for_customer, None)
        q_reject.reject(self.user_for_customer)
        SessionQuote.objects.get(pk=q_accept.id,
                                 status=SessionQuote.STATUS_ACCEPTED)
        SessionQuote.objects.get(pk=q_reject.id,
                                 status=SessionQuote.STATUS_REJECTED)

        self.assertTrue(q_accept.accepted_rejected_by is not None)
        self.assertTrue(q_accept.accepted_rejected_at is not None)
        self.assertTrue(q_reject.accepted_rejected_by is not None)
        self.assertTrue(q_reject.accepted_rejected_at is not None)

        # ----- cancel() -----

        # Check that cancel() doesn't work for invalid users
        for invalid_user in (self.other_photographer,
                             self.user_for_other_customer,
                             self.user_for_customer):
            self.assertRaises(AssertionError, q_accept.cancel, invalid_user)
            self.assertRaises(AssertionError, q_reject.cancel, invalid_user)

    def test_accept_alternative_quote(self):
        count = SessionQuote.objects.all().count()
        # q1
        q_accept_1 = self._create_quote()
        self._create_quote_alternatives(q_accept_1)
        q_accept_1 = SessionQuote.objects.all().get(pk=q_accept_1.id)
        self.assertEqual(q_accept_1.status, SessionQuote.STATUS_QUOTING)

        # q2
        q_accept_2 = self._create_quote()
        self._create_quote_alternatives(q_accept_2)
        q_accept_2 = SessionQuote.objects.all().get(pk=q_accept_2.id)
        self.assertEqual(q_accept_2.status, SessionQuote.STATUS_QUOTING)

        # checks
        self.assertEqual(SessionQuote.objects.all().count(), count + 2)

        q_accept_1.confirm(self.photographer)
        q_accept_2.confirm(self.photographer)
        self.assertEqual(q_accept_1.status, SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)
        self.assertEqual(q_accept_2.status, SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)

        q_accept_1.accept(self.user_for_customer, None)

        self.assertEqual(q_accept_1.status, SessionQuote.STATUS_ACCEPTED)
        self.assertEqual(q_accept_2.status, SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE)

        def _c():
            self.assertEqual(q_accept_2.status, SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE,
                             'Invalid status: ' + q_accept_2.get_status_display())

        self.assertRaises(AssertionError, q_accept_2.accept, self.user_for_customer, (1, 2, 3))
        _c()
        self.assertRaises(AssertionError, q_accept_2.accept, self.user_for_customer, [1, 2, 3])
        _c()
        self.assertRaises(AssertionError, q_accept_2.accept, self.user_for_customer, (1, 2))
        _c()
        self.assertRaises(AssertionError, q_accept_2.accept, self.user_for_customer, (1, 2.2))
        _c()

        self.assertRaises(SessionQuoteAlternative.DoesNotExist,
                          q_accept_2.accept,
                          self.user_for_customer,
                          SessionQuoteAlternative.objects.all().order_by('-id')[0].id + 1)

        q_accept_2.accept(self.user_for_customer, q_accept_2.quote_alternatives.all()[0].id)
        self.assertEqual(q_accept_2.status, SessionQuote.STATUS_ACCEPTED)

    def test_get_waiting_for_customer_response(self):
        try:
            SessionQuote.objects.get_waiting_for_customer_response(self.photographer)
            raise Exception("get_waiting_for_customer_response() didn't failed "
                            "with uesr {}".format(self.photographer))
        except AssertionError:
            pass


class YearMonthIteratorTests(TestCase):

    def test_dont_fail_with_valid_combinatios(self):
        list(year_month_iterator(2000, 1, 2000, 12))
        list(year_month_iterator(2000, 1, 2000, 2))
        list(year_month_iterator(2000, 1, 2000, 1))
        list(year_month_iterator(2000, 1, 2001, 12))
        list(year_month_iterator(2000, 1, 2001, 1))
        list(year_month_iterator(2000, 6, 2001, 1))

    def test_fail_with_valid_combinatios(self):

        with self.assertRaises(AssertionError):
            list(year_month_iterator(2000, 2, 2000, 1))

        with self.assertRaises(AssertionError):
            list(year_month_iterator(2001, 1, 2000, 12))

        with self.assertRaises(AssertionError):
            list(year_month_iterator(2001, 1, 2000, 1))

        with self.assertRaises(AssertionError):
            list(year_month_iterator(2001, 12, 2000, 1))

    def test_return_valid_ranges(self):
        self.assertListEqual(
            list(year_month_iterator(2000, 1, 2000, 1)),
            [(2000, 1)]
        )

        self.assertListEqual(
            list(year_month_iterator(2000, 12, 2000, 12)),
            [(2000, 12)]
        )

        self.assertListEqual(
            list(year_month_iterator(2000, 3, 2000, 6)),
            [(2000, 3), (2000, 4), (2000, 5), (2000, 6)]
        )

        self.assertListEqual(
            list(year_month_iterator(2000, 9, 2001, 1)),
            [(2000, 9), (2000, 10), (2000, 11), (2000, 12), (2001, 1)]
        )

        self.assertListEqual(
            list(year_month_iterator(2000, 9, 2001, 2)),
            [(2000, 9), (2000, 10), (2000, 11), (2000, 12), (2001, 1), (2001, 2)]
        )

        self.assertListEqual(
            list(year_month_iterator(2000, 12, 2001, 2)),
            [(2000, 12), (2001, 1), (2001, 2)]
        )
