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
    return [Notification("a notification for photog", link="/"),
            Notification("another notification for photog")]


def get_customer_notifications(user):
    assert user.is_for_customer()
    return [Notification("a notification for customer", link="/"),
            Notification("another notification for customer")]
