from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('bluebell',
    url('^$', 'consumer.views.home'),
    url('^localize_stations/$', 'consumer.views.localize_stations'),
    url('^zipcode_listings/$', 'consumer.views.zipcode_listings'),
    url('^episode_listings/$', 'consumer.views.episode_listings'),
    url('^listings/feed/(?P<feed_id>\d+)/$', 'consumer.views.feed_listings', name='feed-listings'),
    url('^stations/(?P<station_id>\d+)/$', 'consumer.views.view_station', name='view-station'),

)
