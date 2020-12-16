from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import IntegrityError
from django.contrib.auth.hashers import make_password

from apps.accounts.models import UserProfile
from apps.survey.models import SurveyIdCode, SurveyUser


class Command(BaseCommand):
    help = "Creates new users in bulk, suitable for testing."

    def add_arguments(self, parser):
        parser.add_argument('num_users', type=int)

    def handle(self, *args, **options):
        User = get_user_model()

        for i in range(options['num_users']):
            try:
                user = User.objects.create_user(
                    username='test{0}'.format(i),
                    password='password',
                )
            except IntegrityError:
                print('user{0} already exists, skipping'.format(i))
                continue

            survey_user = SurveyUser.objects.create(
                user=user,
                name='Tester 3'
            )

            s = SurveyIdCode.objects.create(
                idcode=5000+i,
                fodelsedatum='1950',
                surveyuser_global_id=survey_user
            )

            UserProfile.objects.create(
                user=user,
                year_of_birth=1950,
                idcode=s.idcode
            )
