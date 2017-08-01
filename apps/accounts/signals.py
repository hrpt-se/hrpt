from django.dispatch import receiver
from registration.signals import user_activated, user_registered

from apps.accounts.models import user_profile
from apps.survey.models import SurveyUser
from forms import *


@receiver(user_registered)
def user_created(sender, user, request, **kwargs):
    """
    This signal is sent by the registration module when a new user is
    registered (before activation). This handler takes care of creating a
    user_profile instance for the new user.
    """
    form = CaptchaUnicodeRegistrationForm(request.POST)

    user_profile.objects.create(
        user=user,
        yearofbirth=form.data['yearofbirth'],
        idcode=form.data['idcode']
    )


@receiver(user_activated)
def user_activated(sender, user, request, **kwargs):
    """
    This signal is sent by the registration module when a user is activated.
    This handler takes care of creating a SurveyUser instance for the new user.
    It will also update the used SurveyIdCode with the information from the
    form.
    """
    profile = user_profile.objects.get(user=user)

    survey_user = SurveyUser.objects.create(
        user=user,
        name=user.username
    )

    idcode = SurveyIdCode.objects.get(idcode=profile.idcode)
    idcode.fodelsedatum = profile.yearofbirth
    idcode.surveyuser_global_id = survey_user
    idcode.save()
