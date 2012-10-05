from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('bluebell.consumer.views',
    url('^$', 'locator.home', name='home'),
    url('^test?/$', 'locator.test', name='test'),
    url('^station_by_zip/$', 'locator.station_by_zip', name='station_by_zip'),
    url('^station_by_state/$', 'locator.station_by_state', name='station_by_state'),
    url('^stations/(?P<station_id>\d+)/$', 'locator.view_station', name='view-station'),
    url('^listings/(?P<callsign>\w+)/$', 'tvss.listings', name='listings'),
    url('^program/(?P<program_id>\d+)/(?P<callsign>\w+)/$', 'tvss.view_program', name='view-program'),
    url('^show/(?P<show_id>\w+)/(?P<callsign>\w+)/$', 'tvss.view_show', name='view-show'),
    url('^search/(?P<callsign>\w+)/$', 'tvss.search', name='search'),
)
