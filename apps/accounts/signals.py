from django.dispatch import receiver
from registration.signals import user_registered

from apps.accounts.models import user_profile
from apps.survey.models import SurveyUser
from forms import *


@receiver(user_registered)
def user_created(sender, user, request, **kwargs):
    """
    This signal is sent by the registration module when a new user is
    registered (before activation). This handler takes care of creating a
    user_profile- and a SurveyUser instance for the new user. It will also
    update the used SurveyIdCode with the information from the form.
    """
    form = CaptchaUnicodeRegistrationForm(request.POST)

    profile = user_profile.objects.create(
        user=user,
        yearofbirth=form.data['yearofbirth'],
        idcode=form.data['idcode']
    )

    survey_user = SurveyUser.objects.create(
        user=user,
        name=user.username
    )

    idcode = SurveyIdCode.objects.get(idcode=profile.idcode)
    idcode.fodelsedatum = profile.yearofbirth
    idcode.surveyuser_global_id = survey_user
    idcode.save()
