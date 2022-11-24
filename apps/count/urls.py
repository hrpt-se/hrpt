from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^counter', views.counter, name='counter'),
]
