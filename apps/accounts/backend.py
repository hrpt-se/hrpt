from django.db import transaction
from django_registration.backends.activation.views import ActivationView
from django_registration.exceptions import ActivationError, RegistrationError
from django_registration.backends.activation.views import ActivationView
from apps.survey.models import SurveyUser, SurveyIdCode
from .models import UserProfile


class TweakedDefaultActivationView(ActivationView):
    """
    This view is responsible for setting a user as active once the user
    follows the activation link from the mail received when signing up given
    that a series of criteria is met.

    Criteria for successful activation:
      - The link should contain a valid activation link. If not: Abort with a
        warning to the user.
      - The user should not be activated already. If it is: Proceed as normal
        and invite the user to login.
      - The specified idcode for the user should not already be registered to
        another user*. If it is: Abort with a warning to the user.

    *This circumstance can occur if two accounts are registered using the same
    idcode, without activating them. The first account can be successfully
    activated but the second will fail, since the idcode is now occupied by the
    first user.
    """
    @transaction.atomic
    def activate(self, request, activation_key):
        # Get the username from the key and validate that it has not expired.
        username = self.validate_key(activation_key)

        # Get the user and validate that it has not already been activated.
        # If the user is already activated return success.
        try:
            user = self.get_user(username)
        except ActivationError as activation_error:
            if activation_error.code != "already_activated":
                raise activation_error
            return

        profile = UserProfile.objects.get(user=user)
        idcode = SurveyIdCode.objects.get(idcode=profile.idcode)

        # If the idcode is already assigned to another user.
        if idcode.surveyuser_global_id is not None:
            raise ActivationError(self.INVALID_KEY_MESSAGE)

        # Set the user as active.
        user.is_active = True
        user.save()

        survey_user = SurveyUser.objects.create(user=user, name=user.username)

        idcode.fodelsedatum = profile.year_of_birth
        idcode.surveyuser_global_id = survey_user
        idcode.save()

        return user
