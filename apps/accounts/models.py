#Model for storing the code the user provides wtih registration
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


class user_profile(models.Model):
    user=models.ForeignKey(User, unique=True)
    yearofbirth=models.IntegerField()
    idcode=models.CharField(max_length=10)

    def __unicode__(self):
        return u'%s %s' % (self.user, self.idcode)


class UsedActivationKeys(models.Model):
    """
    Not the most orthodox solution, but I do not want to impact the registration_profile
    model, since it is defined and used inside django registration module.
    """
    user = models.ForeignKey(
        User,
        unique=True,
        verbose_name=_('user'),
        on_delete=models.CASCADE
    )

    activation_key = models.CharField(
        _('activation key'),
        max_length=40,
        db_index=True
    )
