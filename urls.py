from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView, TemplateView
from django.views.defaults import page_not_found
from django.conf import settings
from django.views.static import serve

from apps.ew_contact_form.forms import CaptchaContactForm

from django.contrib import admin

from registration.views import RegistrationView
from contact_form.views import ContactFormView
from apps.pollster.views import map_tile, map_click, chart_data
from apps.partnersites.views import colors_css

from views import server_error

admin.autodiscover()

urlpatterns = [
    url(r'^admin/cms/page/18/edit-plugin/[0-9]+/.*escapeHtml.*icon_src.*/$', page_not_found),
    url(r'^admin/manual-newsletters/', include('apps.reminder.nladminurls')),
    url(r'^admin/surveys-editor/', include('apps.pollster.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/tile/(?P<z>\d+)/(?P<x>\d+)/(?P<y>\d+)$', map_tile, name='pollster_map_tile'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)/click/(?P<lat>[\d.-]+)/(?P<lng>[\d.-]+)$', map_click, name='pollster_map_click'),
    url(r'^surveys/(?P<survey_shortname>.+)/charts/(?P<chart_shortname>.+)\.json$', chart_data, name='pollster_chart_data'),
    url(r'^survey/', include('apps.survey.urls')),
    url(r'^reminder/', include('apps.reminder.urls')),
    url(r'^googlec96088c11ef7e5c4.html$', TemplateView.as_view(template_name='googlec96088c11ef7e5c4.html')),
    url(r'^nejtack', RedirectView.as_view(url='https://reply.surveygenerator.com/go.aspx?U=22277ih5v4DGFEKv7gWjt')),
    url(r'^registrera/$', RedirectView.as_view(url='/sv/accounts/register')),

    url(r'^captcha/', include('captcha.urls')),

    url(r'^accounts/', include('apps.accounts.urls')),
    url(r'^login/$', RedirectView.as_view(url=settings.LOGIN_URL), name='loginurl-index'),
    url(r'^login/', include('loginurl.urls')),
    url(r'^count/', include('apps.count.urls')),

    url(r'^contact/$', ContactFormView.as_view(
        form_class=CaptchaContactForm
    ), name='contact_form'),
    url(r'^contact/sent/$', TemplateView.as_view(template_name='contact_form/contact_form_sent.html'), name='contact_form_sent'),

    url(r'^colors.css$', colors_css),

    url(r'^register/$',
        RegistrationView.as_view(
            template_name='registration/registration_explanation.html'
        ),
        name='registration_register_explanation'),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^404/$', page_not_found),
        url(r'^500/$', server_error),
        url(r'upload/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns


# Catchall
urlpatterns += i18n_patterns(url(r'^', include('cms.urls')))

handler500 = 'views.server_error'
