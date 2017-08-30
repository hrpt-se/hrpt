from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^thanks/$', views.thanks, name='survey_thanks'),
    url(r'^thanks_profile/$', views.thanks_profile, name='profile_thanks'),
    url(r'^people/$', views.people, name='survey_people'),
    url(r'^people/add/$', views.people_add, name='survey_people_add'),
    url(r'^people/edit/$', views.people_edit, name='survey_people_edit'),
    url(r'^people/remove/$', views.people_remove, name='survey_people_remove'),
    url(r'^select/$', views.select_survey_user, name='survey_select_user'),
    url(r'^idcode_save/$', views.idcode_save, name='survey_idcode_save'),
    url(r'^idcode_open/$', views.idcode_open, name='survey_idcode_open'),
    url(r'^show/(?P<survey_short_name>.+)/$', views.show_survey, name='survey_show'),
]
