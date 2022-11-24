from datetime import datetime

from django.core.management.base import BaseCommand
from django.core.mail import send_mail

from ...models import get_prev_reminder, get_settings


class Command(BaseCommand):
    help = "Ensure that it's possible to send a reminder, and remind " \
           "specific people if this is not the case"

    def add_arguments(self, parser):
        parser.add_argument('--editor-email',
                            action='append',
                            dest='editor_emails',
                            help='The email addresses of the receipients, '
                                 'supply multiple times for multiple '
                                 'email addresses')

    def handle(self, *args, **options):
        editor_emails = options.get('editor_emails', [])
        if not editor_emails:
            raise Exception("Supply editor emails")

        if get_settings() and get_settings().send_reminders and not get_prev_reminder(datetime.now()):
            send_mail('No reminder message found', """Hi,
            
We can't find any NewsLetter message to send. We need one since the sending of reminders is turned on. You may want to check if your message is published.

This automated message is sent daily until a reminder is found, or the sending of reminders is turned off.""", None,
            editor_emails, fail_silently=False)

