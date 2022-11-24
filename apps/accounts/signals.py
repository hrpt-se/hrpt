from django.dispatch import receiver
from django_registration.signals import user_registered

from apps.accounts.models import UserProfile
from .forms import CaptchaUnicodeRegistrationForm


@receiver(user_registered)
def user_registered(sender, user, request, **kwargs):
    """
    This signal is sent by the registration module when a new user is
    registered (before activation). This handler takes care of creating a
    user_profile instance for the new user.
    """
    form = CaptchaUnicodeRegistrationForm(request.POST)

    UserProfile.objects.create(
        user=user,
        year_of_birth=form.data['year_of_birth'],
        idcode=form.data['idcode']
    )
