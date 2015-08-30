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
    return []
