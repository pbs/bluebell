from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
    url(r'^', include('bluebell.consumer.urls')),
)
