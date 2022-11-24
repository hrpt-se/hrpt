from django.db import transaction
from django_registration.exceptions import ActivationError
from django_registration.backends.activation.views import ActivationView, RegistrationView

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

        # Remove the UserProfile after the user has been activated.
        # profile.delete()
        self._cleanup(idcode.idcode, profile)

        return user

    def _cleanup(self, code, profile):
        # Remove the UserProfile after the user has been activated.
        profile.delete()

        # Remove any UserProfiles and related auth.User that have the same
        # idcode as the activated user since they can never be activated.
        profiles = UserProfile.objects.filter(idcode=code)
        for p in profiles:
            # Make sure that the auth.User is not active and does not have any SurveyUser
            if not p.user.is_active and not p.user.surveyuser_set.all().exists():
                p.user.delete()
            p.delete()


class TweakedRegistrationView(RegistrationView):
    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        if self.request.method == "GET":
            code = self.request.GET.get("code", None)
            if code:
                form.initial["idcode"] = code
            year = self.request.GET.get("year", None)
            if year:
                form.initial["year_of_birth"] = year
        return form
