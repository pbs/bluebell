from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from bluebell.consumer.browser import (
    navigate_to_callsigns,
    navigate_to_feed,
    navigate_to_listings,
)
from bluebell.consumer.extractor import (
    get_localization_callsigns_data,
    get_listing_callsigns_data,
    get_feed_data,
    get_listing_data,
)


def home(request):
    return render_to_response('home.html', {})


def localize_stations(request):
    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        context['zipcode'] = zipcode
        callsigns_page = navigate_to_callsigns(
            settings.SODOR_ENDPOINT, zipcode
        )
        ztc_data = get_localization_callsigns_data(callsigns_page, zipcode)
        context['ztc_data'] = ztc_data

    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def show_listings(request):
    context = {}
    listings = []
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        callsigns_page = navigate_to_callsigns(
            settings.SODOR_ENDPOINT, zipcode
        )
        callsigns_feed_data = get_listing_callsigns_data(
            callsigns_page, zipcode
        )
        feeds = {}
        for callsigns_feed in callsigns_feed_data:
            for callsign, feed_url in callsigns_feed.iteritems():
                callsigns = {}
                feeds_page = navigate_to_feed(feed_url)
                feed_listing_data = get_feed_data(feeds_page)
                for feed_listing in feed_listing_data:
                    feeds_list = []
                    for feed_name, listing_url in feed_listing.iteritems():
                        listings_page = navigate_to_listings(listing_url)
                        listings_data = get_listing_data(listings_page)
                        feeds.setdefault(feed_name, []).extend(listings_data)
                        feeds_list.append(feeds)
                callsigns[callsign] = feeds_list
                listings.append(callsigns)
    context['listings'] = listings

    return render_to_response(
        'show_listings.html',
        context,
        context_instance=RequestContext(request)
    )
