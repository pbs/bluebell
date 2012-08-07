from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('bluebell',
    url('^$', 'consumer.views.home'),
    url('^localize_stations/$', 'consumer.views.localize_stations'),
    url('^zipcode_listings/$', 'consumer.views.zipcode_listings'),
    url('^episode_listings/$', 'consumer.views.episode_listings'),
)
