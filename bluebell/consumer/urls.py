from django.conf.urls import url
from bluebell.consumer.views import locator, tvss

urlpatterns = [
    url('^$', locator.home, name='home'),
    url('^station_by_zip/$', locator.station_by_zip, name='station_by_zip'),
    url('^station_by_zip/(?P<zip>\d+)/$', locator.station_by_zip, name='station_by_zip'),
    url('^station_by_state/$', locator.station_by_state, name='station_by_state'),
    url('^station_by_state/(?P<state>\w+)/$', locator.station_state, name='station_state'),
    url('^station_by_ip/(?P<ip>[0-9\.]+)/$', locator.station_by_ip, name='station_by_ip'),
    url('^station_by_geo/$', locator.station_by_geo, name='station_by_geo'),

    url('^stations/(?P<station_id>\d+)/$', locator.view_station, name='view-station'),
    url('^listings/(?P<callsign>\w+)/$', tvss.listings, name='listings'),
    url('^program/(?P<program_id>\d+)/(?P<callsign>\w+)/$', tvss.view_program, name='view-program'),
    url('^show/(?P<show_id>\w+)/(?P<callsign>\w+)/$', tvss.view_show, name='view-show'),
    url('^search/(?P<callsign>\w+)/$', tvss.search, name='search'),
]
