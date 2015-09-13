from django.core.urlresolvers import reverse

from lumina import models


class Notification:

    def __init__(self, message, link=None):
        self._message = message
        self._link = link

    @property
    def message(self):
        return self._message

    @property
    def link(self):
        return self._link


def get_photographer_notifications(user):
    assert user.is_photographer()
    notifications = []

    pending_uploads_count = models.ImageSelection.objects.full_quality_pending_uploads(user).count()

    if pending_uploads_count > 0:
        if pending_uploads_count == 1:
            msg = "Hay 1 sesión fotográfica esperando a que se suban imágenes"
        else:
            msg = "Hay {} sesiones fotográficas esperando a que se suban imágenes".format(pending_uploads_count)
        notifications.append(Notification(msg, link=reverse('imageselection_with_pending_uploads_list')))

    return notifications


def get_customer_notifications(user):
    assert user.is_for_customer()
    notifications = []

    # ----- Presupuestos por aprobar -----

    quotes_pending_count = models.SessionQuote.objects.get_waiting_for_customer_response(user).count()
    if quotes_pending_count == 1:
        notifications.append(Notification(
            "Hay 1 presupuesto pendiente de aprobación",
            link=reverse('quote_list_pending_for_customer')))
    elif quotes_pending_count > 1:
        notifications.append(Notification(
            "Hay {} presupuestos pendientes de aprobación".format(quotes_pending_count),
            link=reverse('quote_list_pending_for_customer')))

    # ----- Peticiones de selección de fotos pendientes -----

    image_selection_pending_count = models.ImageSelection.objects.pending_image_selections(user).count()
    if image_selection_pending_count == 1:
        notifications.append(Notification(
            "Hay 1 petición de selección de imágenes pendiente",
            link=reverse('imageselection_list')))
    elif image_selection_pending_count > 1:
        notifications.append(Notification(
            "Hay {} peticiones de selección de imágenes pendientes".format(image_selection_pending_count),
            link=reverse('imageselection_list')))

    return notifications
