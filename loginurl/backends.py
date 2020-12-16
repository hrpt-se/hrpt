from django.contrib.auth.models import User

from loginurl.models import Key


class LoginUrlBackend:
    """
    Authentication backend that checks the given ``key`` to a record in the
    ``Key`` model. If the record is found, then ``is_valid()`` method is called
    to check if the key is still valid.
    """
    supports_object_permissions = False
    supports_anonymous_user = False

    def authenticate(self, request, key=None):
        """
        Check if the key is valid.
        """
        data = Key.objects.filter(key=key).first()
        return data.user if data else None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
