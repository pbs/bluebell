import re
import json
import urllib
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from bluebell.consumer.browser import (
    navigate_to_callsigns,
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
        date = request.POST.get('date')
        time = request.POST.get('time')
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
                    feeds_page = _read_data(feed_url)
                    feed_listing_data = get_feed_data(feeds_page)
                    callsigns = {}
                    feeds = {}
                    for feed_listing in feed_listing_data:
                        for feed_name, filter_url in feed_listing.iteritems():
                            listings_data = _get_listings_by_date(
                                filter_url, date, time
                            )
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


def _get_listings_by_date(filter_url, date, time):
    input_month, input_day, input_year = date.split('-')
    url_date_format = input_year + input_month + input_day
    filter_url = re.sub(
        '{date}.json', url_date_format + '.json', filter_url
    )
    listings_by_date_page = _read_data(filter_url)
    listings_data = get_listing_data(
        listings_by_date_page, date, time
    )
    return listings_data


def _read_data(url):
    try:
        response = json.loads(urllib.urlopen(url).read())
    except ValueError:
        return None
    else:
        return response
