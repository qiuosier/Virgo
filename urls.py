from django.conf.urls import url

from . import views

app_name = 'virgo'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^candle/(?P<symbol>[\w\-]+)/$', views.candle_stick, name='candle_stick'),
    url(r'^candle/(?P<symbol>[\w\-]+)/(?P<start>[0-9]+-[0-9]+-[0-9])/$', views.candle_stick, name='candle_stick'),
    url(r'^update/sp500/$', views.update_sp500, name='update_sp500'),
    url(r'^update/symbols/$', views.update_symbols, name='update_symbols'),
    url(r'^update/next/$', views.update_next, name='update_next')
]
