from django.core.management.base import BaseCommand

from apps.pollster import models

class Command(BaseCommand):
    help = 'Register a question data type.'

    def add_arguments(self, parser):
        parser.add_argument('-t',
                            '--title',
                            action='store',
                            type=str,
                            dest='title',
                            help='Data type title.')

        parser.add_argument('-d',
                            '--dbtype',
                            action='store',
                            type=str,
                            dest='dbtype',
                            help='Database type.')

        parser.add_argument('-j',
                            '--jsclass',
                            action='store',
                            type=str,
                            dest='jsclass',
                            help='JavaScript class.')

        parser.add_argument('-c',
                            '--cssclass',
                            action='store',
                            type=str,
                            dest='cssclass',
                            help='CSS class.')

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity'))

        data = models.QuestionDataType()
        data.title = options.get('title')
        data.db_type = options.get('dbtype', None)
        data.js_class = options.get('jsclass', None)
        data.css_class = options.get('cssclass', None)
        data.save()

        if verbosity > 0:
            print('Question data type "%s" registered' % (data,))

