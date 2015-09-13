import logging

from django.conf import settings
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from lumina.models import SessionQuote

logger = logging.getLogger(__name__)


def send_emails(subject, to_email_list, body):
    if not to_email_list:
        return

    logger.info("Sending email '{}' to '{}'".format(subject, to_email_list))
    from_email = "Lumina <notifications@lumina-photo.com.ar>"
    try:
        send_mail(subject, body, from_email, to_email_list, fail_silently=False)
        logger.info("Email to %s, with subject '%s' queued", to_email_list, subject)
    except:
        logger.exception("Couldn't queue email to %s", to_email_list)
        if settings.DEBUG:
            raise


def send_email(subject, to_email, body):
    return send_emails(subject, [to_email], body)


def send_email_for_session_quote(quote, user, request):
    """
    Send an email informing the change of status of SessionQuote.
    The new status is taken from quote.status
    """
    link = request.build_absolute_uri(reverse('quote_detail', args=[quote.id]))

    to_email_list_for_customers = []
    for an_user in quote.customer.users.all():
        if an_user.get_or_create_user_preferences().send_emails:
            logger.info("send_email_for_session_quote(): user '%s' (CUSTOMER) wants to receive emails", an_user)
            to_email_list_for_customers.append(an_user.email)
        else:
            logger.info("send_email_for_session_quote(): user '%s' (CUSTOMER) don't want to receive emails", an_user)

    to_email_list_for_photographers = []
    for an_user in quote.studio.photographers.all():
        if an_user.get_or_create_user_preferences().send_emails:
            logger.info("send_email_for_session_quote(): user '%s' (PHOTOGR) wants to receive emails", an_user)
            to_email_list_for_photographers.append(an_user.email)
        else:
            logger.info("send_email_for_session_quote(): user '%s' (PHOTOGR) don't want to receive emails", an_user)

    if quote.status == SessionQuote.STATUS_WAITING_CUSTOMER_RESPONSE:
        # send to customer
        subject = "Ud. posee un nuevo presupuesto"
        body = ("Ud. posee un nuevo presupuesto.\n"
                "Para verlo, acceda a {}.\n"
                "".format(link))
        send_emails(subject, to_email_list_for_customers, body)

        # send to photographers
        subject = "Se ha enviado un presupuesto"
        body = ("Se ha enviado un presupuesto.\n"
                "Cliente: {}.\n"
                "Enviado por: {}.\n"
                "Para verlo, acceda a {}."
                "".format(quote.customer, user, link))
        send_emails(subject, to_email_list_for_photographers, body)

    elif quote.status == SessionQuote.STATUS_ACCEPTED:
        # send to customer
        subject = "Se ha aceptado un presupuesto"
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list_for_customers, body)

        # send to photographers
        subject = "Un cliente ha aceptado un presupuesto"
        body = ("Se ha aceptado un presupuesto.\n"
                "El presupuesto fue aceptado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list_for_photographers, body)

    elif quote.status == SessionQuote.STATUS_REJECTED:
        # send to customer
        subject = "Se ha rechazado un presupuesto"
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list_for_customers, body)

        # send to photographers
        subject = "Un cliente ha rechazado un presupuesto"
        body = ("Se ha rechazado un presupuesto.\n"
                "El presupuesto fue rechazado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list_for_photographers, body)

    elif quote.status == SessionQuote.STATUS_CANCELED:
        # send to photographers
        subject = "Se ha cancelado un presupuesto"
        body = ("Se ha cancelado un presupuesto.\n"
                "El presupuesto fue cancelado por {}.\n"
                "Para verlo, acceda a {}."
                "".format(user, link))
        send_emails(subject, to_email_list_for_photographers, body)

    elif quote.status == SessionQuote.STATUS_QUOTING:
        pass

    else:
        logger.error("send_email_for_session_quote(): Invalid quote.status: '%s'", quote.status)
        return
