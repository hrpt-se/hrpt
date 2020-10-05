from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Register a virtual option type.'

    def add_arguments(self, parser):
        parser.add_argument('-t',
                            '--title',
                            action='store',
                            type=str,
                            dest='title',
                            help='Rule title.')

        parser.add_argument('-q',
                            '--question-data-type-title',
                            action='store',
                            type=str,
                            dest='question_data_type_title',
                            help='Question data type title')

        parser.add_argument('-j',
                            '--jsclass',
                            action='store',
                            type=str,
                            dest='jsclass',
                            help='JavaScript class.')

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        question_data_type_title = options.get('question_data_type_title')
        question_data_type = models.QuestionDataType.objects.get(title = question_data_type_title)

        data = models.VirtualOptionType()
        data.question_data_type = question_data_type
        data.title = options.get('title')
        data.js_class = options.get('jsclass', None)
        data.save()

        if verbosity > 0:
            print('Rule type "%s" registered' % (data,))
