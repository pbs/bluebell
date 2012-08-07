import re
import json
import urllib
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from bluebell.consumer.extractor import (
    get_localization_callsigns_data,
    get_listing_callsigns_data,
    get_feed_data,
    get_listing_data,
)

from resty import client


def home(request):
    return render_to_response('home.html', {})


def localize_stations(request):
    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        context['zipcode'] = zipcode

        services_data = _read_data(settings.SODOR_ENDPOINT)
        zipcode_collection_url = (
            services_data['$services']['zipcodes']['$filters']['zip']
        )
        zipcode_collection_url = (
            re.sub('{zipcode}', zipcode, zipcode_collection_url)
        )
        zipcode_collection_data = _read_data(zipcode_collection_url)

        if (not zipcode_collection_data or
            zipcode_collection_data['$items'] == []):
            return render_to_response(
                'localize_stations.html',
                context,
                context_instance=RequestContext(request)
            )

        callsign_by_zip_url = (
            zipcode_collection_data['$items'][0]['$links'][0]['$self']
        )
        callsigns_page = _read_data(callsign_by_zip_url)
        ztc_data = get_localization_callsigns_data(callsigns_page, zipcode)
        context['ztc_data'] = ztc_data

    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def zipcode_listings(request):
    context = {}
    listings = []
    headends_data = []
    selected_headend = False
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        date = request.POST.get('date')
        time = request.POST.get('time')
        channels_url = request.POST.get('channels_url')
        context['zipcode'] = zipcode

        input_month, input_day, input_year = date.split('-')
        url_date_format = input_year + input_month + input_day

        services_data = _read_data(settings.SODOR_ENDPOINT)
        zipcode_collection_url = (
            services_data['$services']['zipcodes']['$filters']['zip']
        )
        zipcode_collection_url = (
            re.sub('{zipcode}', zipcode, zipcode_collection_url)
        )

        try:
            zipcode_data = client.load(zipcode_collection_url)
        except KeyError:
            pass
        else:
            if zipcode_data.items():
                headends = zipcode_data.items()[0].related('presence')
                for headend in headends.items():
                    headends_data.append(
                        (headend.content.name, headend.related('children').self)
                    )
            context['headends'] = headends_data

        zipcode_collection_data = _read_data(zipcode_collection_url)
        if (not zipcode_collection_data or
            zipcode_collection_data['$items'] == []):
            return render_to_response(
                'show_listings.html',
                context,
                context_instance=RequestContext(request)
            )

        callsign_by_zip_url = (
            zipcode_collection_data['$items'][0]['$links'][0]['$self']
        )
        callsigns_page = _read_data(callsign_by_zip_url)
        callsigns_feed_data = get_listing_callsigns_data(
            callsigns_page, zipcode
        )

        if channels_url:
            selected_headend = True
            callsigns = {}
            feeds = {}
            channels_data = _read_data(channels_url)
            for channel in channels_data['$items']:
                channel_number = channel['cable_number']
                callsign = channel['$links'][0]['$links'][0]['callsign']
                feed_name = channel['$links'][0]['$links'][1]['full_name']
                filter_url = channel['$links'][0]['$links'][2]['$filters']['date']
                listings_data = _get_listings_by_date(
                    filter_url, url_date_format, time
                )
                feeds = {}
                if listings_data:
                    listings_data.insert(0, channel_number)
                    feeds[feed_name] = listings_data
                if feeds:
                    callsigns.setdefault(callsign, []).append(feeds)
            listings = [{key:val} for key, val in callsigns.iteritems()]
            context['listings'] = listings
            context['selected_headend'] = selected_headend
            context['selected_channels_url'] = channels_url

        else:
            for callsigns_feed in callsigns_feed_data:
                for callsign, feed_url in callsigns_feed.iteritems():
                    feeds_page = _read_data(feed_url)
                    feed_listing_data = get_feed_data(feeds_page)
                    callsigns = {}
                    feeds = {}
                    for feed_listing in feed_listing_data:
                        for feed_name, filter_url in feed_listing.iteritems():
                            listings_data = _get_listings_by_date(
                                filter_url, url_date_format, time
                            )
                            if listings_data:
                                feeds.setdefault(feed_name, []).extend(
                                    listings_data)
                    if feeds:
                        callsigns.setdefault(callsign, []).append(feeds)
                        listings.append(callsigns)
            context['listings'] = listings
            context['selected_headend'] = selected_headend
    print listings
    return render_to_response(
        'zipcode_listings.html',
        context,
        context_instance=RequestContext(request)
    )


def episode_listings(request):

    mock_listings = [
        {'WETA': [
            {'WETA TV':
                ('0010', {'start_time': '1330', 'start_date': '20120807'})
            },
            {'WETA':
                ('0237', {'start_time': '1430', 'start_date': '20120807'})
            },
            {'WMHT HDTV':
                ('0088', {'start_time': '2000', 'start_date': '20120807'})
            },
            {'WETA UK':
                ('0144', {'start_time': '1430', 'start_date': '20120807'})
            },
            {'WETA Kids':
                ('0002', {'start_time': '1430', 'start_date': '20120807'})
            }]
        },
        {'WMPB': [
            {u'Maryland Public Television':
                ('0012', {'start_time': '1500', 'start_date': '20120807'})
            },
            {u'MPT2':
                ('0033', {'start_time': '1830', 'start_date': '20120807'})
            },
            {u'MPT HDTV':
                ('0526', {'start_time': '1730', 'start_date': '20120807'})
            }]
        },
    ]

    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        episode_url = request.POST.get('episode_url')
        context['zipcode'] = zipcode
        context['episode_url'] = episode_url
        #TODO(severb): Populate headends by the given zip.
        context['headends'] =  ['Comcast 1', 'Comcast 2']
        #TODO(severb): Extract ep title based on the input url.
        context['episode_title'] = 'Episode Title'
        #TODO(severb): Qurey sodor API to get real data.
        context['listings'] = mock_listings

    return render_to_response(
        'episode_listings.html',
        context,
        context_instance=RequestContext(request)
    )


def _get_listings_by_date(filter_url, date, time):
    filter_url = re.sub(
        '{date}.json', date + '.json', filter_url
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
