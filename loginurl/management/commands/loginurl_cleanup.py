from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Clean up expired one time keys."

    def handle_noargs(self, **options):
        from loginurl import utils
        utils.cleanup()

