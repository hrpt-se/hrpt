from registration.views import ActivationView

from registration import signals
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _
import sys


from .models import UsedActivationKeys


class TweakedDefaultActivationView(ActivationView):
    """
    This is a tweaked version of the default registration backend. It leaves almost
    everything untouched, except that it saves the activation keys that have been used "used_act_key"
    in other table.
    This way, we solve the confusing situation where a user would already have
    activated his account, but would get an activation error message.
    """
    def activate(self, request, activation_key):
        #print >> sys.stderr, "into activate!!!!!!!"

        #First we check if the key is used
        try:
            used_act_key = UsedActivationKeys.objects.get(activation_key=activation_key)
            return used_act_key.user
        except UsedActivationKeys.DoesNotExist:
            pass

        activated_user = RegistrationProfile.objects.activate_user(activation_key)
        if activated_user:
            signals.user_activated.send(sender=self.__class__,
                                        user=activated_user,
                                        request=request)
            #save the activation key in other table
            new_used_key = UsedActivationKeys(user=activated_user, activation_key=activation_key)
            new_used_key.save()
        return activated_user

    def get_success_url(self, user):
        return 'registration_activation_complete', (), {}

