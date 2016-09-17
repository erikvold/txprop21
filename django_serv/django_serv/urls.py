from django.conf.urls import include
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$',
        views.index),

    url(r'^payments/',
        include('two1.bitserv.django.urls', namespace='payments')),
]
