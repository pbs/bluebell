from django.conf.urls.defaults import patterns, url


urlpatterns = patterns('bluebell',
    url('^$', 'consumer.views.home'),
    url('^localize_stations/$', 'consumer.views.localize_stations'),
    url('^show_listings/$', 'consumer.views.show_listings'),
)
