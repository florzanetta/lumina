from django.utils.functional import SimpleLazyObject

from lumina import user_notifications as _user_notifications


USER_NOTIFICATIONS_KEY = 'user_notifications'


def user_notifications(request):
    """Set notification for logged-in user"""

    if not request.user.is_authenticated():
        return {}

    if request.user.is_photographer():
        def _get_notifications_for_user():
            return _user_notifications.get_photographer_notifications(request.user)

    elif request.user.is_for_customer():
        def _get_notifications_for_user():
            return _user_notifications.get_customer_notifications(request.user)

    else:
        raise Exception("Invalid type of user")

    return {
        USER_NOTIFICATIONS_KEY: SimpleLazyObject(_get_notifications_for_user)
    }
