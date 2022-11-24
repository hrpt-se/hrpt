from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    This model keeps values from the user registration form that will be
    added to the SurveyUser model when the user account is activated.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    year_of_birth = models.IntegerField()
    idcode = models.CharField(max_length=10)

    def __unicode__(self):
        return '%s %s' % (self.user, self.idcode)

    def __str__(self):
        return self.__unicode__()
