from django.urls import path
from django.conf.urls import url

from . import views

urlpatterns = [
    path('callback', views.callback),
    path('confirm', views.confirm),
    url(r'^confirm', views.confirm),
]
