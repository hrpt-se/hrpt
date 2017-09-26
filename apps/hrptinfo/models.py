from django.db import models

from cms.models import CMSPlugin
from django.utils.encoding import python_2_unicode_compatible
from djangocms_text_ckeditor.fields import HTMLField


@python_2_unicode_compatible
class NewsItem(CMSPlugin):
    title = models.CharField(max_length=255)
    date = models.DateField(auto_now_add=True)
    content = HTMLField()

    def __str__(self):
        return self.title
