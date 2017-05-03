from django.core.management.commands import loaddata
from django.db.models import signals
import cms.models
import cms.signals


class Command(loaddata.Command):
    """ 
    This command is a workaround that fixes an old bug 
    (https://github.com/divio/django-cms/issues/1031) in Django CMS. As soon 
    as Django CMS is updated to the most recent version, this command should be
    removed.
    """
    def handle(self, *fixture_labels, **options):
        signals.post_save.disconnect(
            cms.signals.update_placeholders,
            sender=cms.models.Page
        )

        loaddata.Command.handle(self, *fixture_labels, **options)

        signals.post_save.connect(
            cms.signals.update_placeholders,
            sender=cms.models.Page
        )
