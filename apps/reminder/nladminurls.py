from django.conf.urls import url
from django.conf import settings
from loginurl.views import cleanup, login


from .views import (
    list_newsletter_templates, send_manual_newsletter,
    show_newsletter_template, send_test_email_to_myself,
    show_newsletter_template_in_iframe
)

urlpatterns = [
    url(r'^templates/$', list_newsletter_templates),
    url(r'^send_manual_newsletter/(?P<newsletter_template_id>[0-9]+)/$', send_manual_newsletter),
    url(r'^templates/(?P<id>[0-9]+)/$', show_newsletter_template),
    #This is for debugging emial sending.
    url(r'^templates/send_to_myself/(?P<newsletter_template_id>[0-9]+)/$', send_test_email_to_myself),
    url(r'^templates/iframed/(?P<id>[0-9]+)/$', show_newsletter_template_in_iframe)
]
