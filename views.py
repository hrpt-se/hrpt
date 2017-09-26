from django.conf import settings
from django import http
from django.template import Context, loader, RequestContext
from django.shortcuts import render_to_response
from django import forms
from django.contrib.auth import authenticate, login
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db import connection
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse, NoReverseMatch

from apps.survey.models import SurveyUser
from loginurl.utils import create as create_login_key

def server_error(request, template_name='500.html'):
    """
    500 error handler.

    Templates: `500.html`
    Context:
        MEDIA_URL
            Path of static media (e.g. "media.example.org")

    Django's standard 500 error handler does not serve MEDIA_URL correctly; this one does
    """
    t = loader.get_template(template_name)
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL
    })))



