import re
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
        context['zipcode'] = zipcode
        callsigns_page = navigate_to_callsigns(
            settings.SODOR_ENDPOINT, zipcode
        )
        callsigns_feed_data = get_listing_callsigns_data(
            callsigns_page, zipcode
        )
        if callsigns_feed_data:
            for callsigns_feed in callsigns_feed_data:
                for callsign, feed_url in callsigns_feed.iteritems():
                    feeds_page = navigate_to_feed(feed_url)
                    feed_listing_data = get_feed_data(feeds_page)
                    callsigns = {}
                    feeds = {}
                    for feed_listing in feed_listing_data:
                        for feed_name, listings_url in feed_listing.iteritems():
                            all_listings_data = _get_all_listings(listings_url)
                            for listings_data in all_listings_data:
                                if listings_data:
                                    feeds.setdefault(feed_name, []).extend(
                                        listings_data)
                    if feeds:
                        callsigns.setdefault(callsign, []).append(feeds)
                        listings.append(callsigns)
            context['listings'] = listings
    return render_to_response(
        'show_listings.html',
        context,
        context_instance=RequestContext(request)
    )


def _get_all_listings(listings_url, all_listings_data = None):
    if all_listings_data is None:
        all_listings_data = []
    listings_page = navigate_to_listings(listings_url)
    page, items_count, page_size, listings_data = get_listing_data(
        listings_page
    )
    total_pages = items_count/page_size
    all_listings_data.append(listings_data)
    while page <= total_pages:
        page = page + 1
        listings_url = re.sub('\d+.json', str(page) + '.json', listings_url)
        return _get_all_listings(listings_url, all_listings_data)
    return all_listings_data
