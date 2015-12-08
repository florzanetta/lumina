# -*- coding: utf-8 -*-

import decimal

from django.test import TestCase
from django.utils import timezone

from lumina.models import SessionQuote, Studio, LuminaUser, SessionQuoteAlternative
from lumina.utils import year_month_iterator


class SessionQuoteModelTests(TestCase):
    fixtures = ['sample/studios.json', 'sample/customers.json', 'sample/users.json']

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
