from django.conf.urls import url

from . import views

app_name = 'virgo'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<symbol>[A-Za-z0-9\-]+)/$', views.candle_stick, name='candle_stick'),
    url(r'^(?P<symbol>[A-Za-z0-9\-]+)/(?P<start>[0-9]+-[0-9]+-[0-9])/$', views.candle_stick, name='candle_stick'),
]
