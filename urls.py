from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve

from contact_form.views import ContactFormView

from apps.partnersites.views import colors_css
from apps.pollster.views import map_tile, map_click, chart_data
from apps.hrptinfo.forms import CaptchaContactForm

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/manual-newsletters/', include('apps.reminder.nladminurls')),
    url(r'^admin/surveys-editor/', include('apps.pollster.urls')),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/tile/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)$',
        map_tile, name='pollster_map_tile'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/click/(?P<lat>[\d.-]+)/(?P<lng>[\d.-]+)$',
        map_click, name='pollster_map_click'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)\.json$', chart_data,
        name='pollster_chart_data'),
    url(r'^survey/', include('apps.survey.urls')),
    url(r'^reminder/', include('apps.reminder.urls')),
    url(r'^registrera/$', RedirectView.as_view(url='/accounts/register')),
    url(r'^accounts/', include('apps.accounts.urls')),
    url(r'^login/', include('loginurl.urls')),
    url(r'^count/', include('apps.count.urls')),
    url(r'^contact/$', ContactFormView.as_view(form_class=CaptchaContactForm), name='contact_form'),
    url(r'^contact/sent/$', TemplateView.as_view(template_name='contact_form/contact_form_sent.html'),
        name='contact_form_sent'),
    url(r'^colors.css$', colors_css)
]

# Catchall
urlpatterns += i18n_patterns(
    url(r'^', include('cms.urls'))
)

if settings.DEBUG:
    urlpatterns = [
                      url(r'^upload/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
                  ] + staticfiles_urlpatterns() + urlpatterns
