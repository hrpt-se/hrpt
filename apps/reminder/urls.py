from django.conf.urls import url

from .views import manage, overview, preview, unsubscribe

urlpatterns = [
    url(r'^unsubscribe/$', unsubscribe, name='unsubscribe'),
    url(r'^overview/$', overview),
    url(r'^manage/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<hour>[0-9]+)/(?P<minute>[0-9]+)/$', manage),
    url(r'^preview/(?P<year>[0-9]+)/(?P<month>[0-9]+)/(?P<day>[0-9]+)/(?P<hour>[0-9]+)/(?P<minute>[0-9]+)/$', preview),
]
