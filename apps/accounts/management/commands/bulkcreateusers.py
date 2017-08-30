from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import IntegrityError

from apps.accounts.models import user_profile
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
                    password='password'
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
                surveyuser_global_id=survey_user
            )

            user_profile.objects.create(
                user=user,
                yearofbirth=1950,
                idcode=s.idcode
            )
