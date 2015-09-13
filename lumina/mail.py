import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from lumina.models import SessionQuote, LuminaUser

logger = logging.getLogger(__name__)


def send_emails_to_users(subject, to_user_list, body):
    """Send emails to a list of user.

    Check user's preferences, send email ONLY to those users that wants to receive emails.
    """
    if not to_user_list:
        return

    to_email_list = []
    for an_user in to_user_list:
        assert isinstance(an_user, LuminaUser)
        if an_user.get_or_create_user_preferences().send_emails:
            logger.info("send_emails_to_users(): user '%s' wants to receive emails", an_user)
            to_email_list.append(an_user.email)
        else:
            logger.info("send_emails_to_users(): user '%s' don't want to receive emails", an_user)

    send_emails(subject, to_email_list, body)


def send_emails(subject, to_email_list, body):
    """Send an email. This method should be used ONLY when the email is NOT sent to an USER.
    To send emails to users, use `send_emails_to_users()`
    """
    logger.info("Sending email '{}' to '{}'".format(subject, to_email_list))
    from_email = "Lumina <notifications@lumina-photo.com.ar>"
    try:
        send_mail(subject, body, from_email, to_email_list, fail_silently=False)
        logger.info("Email to %s, with subject '%s' queued", to_email_list, subject)
    except:
        logger.exception("Couldn't queue email to %s", to_email_list)
        if settings.DEBUG:
            raise


def send_email_for_session_quote(quote, user, request):
    """
    Send an email informing the change of status of SessionQuote.
    The new status is taken from quote.status
    """
    link = request.build_absolute_uri(reverse('quote_detail', args=[quote.id]))

    customers_to_notify = quote.customer.users.all()
    photographers_to_notify = quote.studio.photographers.all()

    if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
        # send to customer
        subject = "Ud. posee un nuevo presupuesto"
        body = ("Ud. posee un nuevo presupuesto.\n"
                "Para verlo, acceda a {}.\n"
                "".format(link))
        send_emails_to_users(subject, customers_to_notify, body)

        # send to photographers
        subject = "Se ha enviado un presupuesto"
        body = ("Se ha enviado un presupuesto.\n"
                "Cliente: {}.\n"
                "Enviado por: {}.\n"
                "Para verlo, acceda a {}."
                "".format(quote.customer, user, link))
        send_emails_to_users(subject, photographers_to_notify, body)

    elif quote.status == SessionQuote.STATUS_ACCEPTED:
        # send to customer
        subject = "Se ha aceptado un presupuesto"
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails_to_users(subject, customers_to_notify, body)

        # send to photographers
        subject = "Un cliente ha aceptado un presupuesto"
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails_to_users(subject, photographers_to_notify, body)

    elif quote.status == SessionQuote.STATUS_REJECTED:
        # send to customer
        subject = "Se ha rechazado un presupuesto"
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails_to_users(subject, customers_to_notify, body)

        # send to photographers
        subject = "Un cliente ha rechazado un presupuesto"
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails_to_users(subject, photographers_to_notify, body)

    elif quote.status == SessionQuote.STATUS_CANCELED:
        # send to photographers
        subject = "Se ha cancelado un presupuesto"
        body = ("Se ha cancelado un presupuesto.\n"
                "El presupuesto fue cancelado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails_to_users(subject, photographers_to_notify, body)

    elif quote.status == SessionQuote.STATUS_QUOTING:
        pass

    else:
        logger.error("send_email_for_session_quote(): Invalid quote.status: '%s'", quote.status)
        return
