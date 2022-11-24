from django.core.management.base import BaseCommand

from apps.pollster import models


class Command(BaseCommand):
    help = 'Update all charts and invalidate tile cache.'

    def handle(self, *args, **options):
        verbosity = int(options.get('verbosity'))

        for chart in models.Chart.objects.all():
            if not chart.update_data():
                print('Chart "%s" update FAILED' % (chart,))
            elif verbosity > 0:
                print('Chart "%s" updated' % (chart,))
