from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Register a rule type.'

    def add_arguments(self, parser):
        parser.add_argument('-t',
                            '--title',
                            action='store',
                            type=str,
                            dest='title',
                            help='Rule title.')

        parser.add_argument('-j',
                            '--jsclass',
                            action='store',
                            type=str,
                            dest='jsclass',
                            help='JavaScript class.')

    def handle(self, *args, **options):
        from apps.pollster import models

        verbosity = int(options.get('verbosity'))

        rule = models.RuleType()
        rule.title = options.get('title')
        rule.js_class = options.get('jsclass', None)
        rule.save()

        if verbosity > 0:
            print('Rule type "%s" registered' % (rule,))

