from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('bluebell',
    url('^$', 'consumer.views.home'),
    url('^localize_stations/$', 'consumer.views.localize_stations'),
    url('^zipcode_listings/$', 'consumer.views.zipcode_listings'),
    url('^episode_listings/$', 'consumer.views.episode_listings'),
    url('^listings/(?P<callsign>\w+)/$', 'consumer.views.listings', name='listings'),
    url('^stations/(?P<station_id>\d+)/$', 'consumer.views.view_station', name='view-station'),
    url('^program/(?P<program_id>\d+)/(?P<callsign>\w+)/$', 'consumer.views.view_program', name='view-program'),
    url('^show/(?P<show_id>\w+)/(?P<callsign>\w+)/$', 'consumer.views.view_show', name='view-show'),
)
