from django.db import transaction
from registration.models import RegistrationProfile
from registration.views import ActivationView

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
        try:
            registration_profile = RegistrationProfile.objects.get(
                activation_key=activation_key)
        except RegistrationProfile.DoesNotExist:
            # If no profile is found, the link is invalid
            return False

        # If the user is already activated, abort further processing
        if registration_profile.user.is_active:
            return registration_profile.user

        profile = UserProfile.objects.get(user=registration_profile.user)
        idcode = SurveyIdCode.objects.get(idcode=profile.idcode)

        # If the idcode is already assigned to another user.
        if idcode.surveyuser_global_id is not None:
            return False

        # Set the user as active.
        # Note that this is not done through the
        # RegistrationManager.activate_user() method by intention. That method
        # will remove the mapping between the activation code and user, making
        # the first step of this view impossible.
        registration_profile.user.is_active = True
        registration_profile.user.save()

        survey_user = SurveyUser.objects.create(
            user=registration_profile.user,
            name=registration_profile.user.username
        )

        idcode.fodelsedatum = profile.year_of_birth
        idcode.surveyuser_global_id = survey_user
        idcode.save()

        return registration_profile.user

    def get_success_url(self, user):
        return 'registration_activation_complete', (), {}
