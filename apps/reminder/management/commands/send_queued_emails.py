from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives

from ...models import FailedEmail, QueuedEmail, SentEmail
from django.utils.html import strip_tags
from ...send import create_message

import time
import traceback


class Command(BaseCommand):
    """
    If called without argunments, this command will never return and it will continuously
    pull entries from QueuedEmail table.

    Probably, the easiest is to run this inside screen and then detach.
    Might be a good idea to redirect the output too.
    """

    help = "Send emails queued manually from a template."

    def add_arguments(self, parser):
        parser.add_argument('--queues',
                            action='store_true',
                            dest='queues',
                            default=False,
                            help='Print debug info')

    def handle(self, *args, **options):
        if options.get('queues'):
            print("QueuedEmail: " + str(QueuedEmail.objects.count()))
            print("SentEmail: " + str(SentEmail.objects.count()))
            print("FailedEmail: " + str(FailedEmail.objects.count()))
            return None

        self.timestamped_print("======= Started email sending job...")

        while True:
            self.timestamped_print(str(QueuedEmail.objects.count()) + " Emails in queue")
            a_bunch_of_queued_email = QueuedEmail.objects.order_by("id")[:60]
            # EvS 2019/04/17 changed limit back to 30 per interval
            for queued_email in a_bunch_of_queued_email:
                try:
                    nl_instance = queued_email.manual_newsletter

                    self.timestamped_print("Sending email to {} (id: {})".format(
                        queued_email.user.email, queued_email.user.id))

                    text_base, html_content = create_message(queued_email.user, nl_instance, "sv")
                    text_content = strip_tags(text_base)

                    msg = EmailMultiAlternatives(
                        queued_email.manual_newsletter.subject,
                        text_content,
                        "%s <%s>" % (nl_instance.sender_name, nl_instance.sender_email),
                        [queued_email.user.email],
                    )

                    msg.attach_alternative(html_content, "text/html")
                    msg.send()

                    sent_email = SentEmail(
                        user=queued_email.user,
                        manual_newsletter=nl_instance,
                        queued = nl_instance.timestamp  # TODO: remove this from the model
                    )

                    queued_email.delete()
                    sent_email.save()

                except Exception as e:
                    self.timestamped_print("FAILED!!!! Stacktrace saved to reminder_failedemail database table")

                    failed_email = FailedEmail(
                        user=queued_email.user,
                        manual_newsletter=nl_instance,
                        message=str(e)[:254],
                        traceback=traceback.format_exc()
                    )

                    failed_email.save()

            interval_seconds = 60
            self.timestamped_print("Wait " + str(interval_seconds) + " seconds...")
            time.sleep(interval_seconds)  # EvS 2016/01/27 changed from 3s to 60s to prevent peak

    def timestamped_print(self, message):
        timenow_readable_string = time.strftime('%Y-%m-%d %H:%M:%S')
        print("[{}]{}".format(timenow_readable_string, message))
