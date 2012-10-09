import os
import re
import json
import urllib
import datetime
from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from dateutil import parser

from bluebell.consumer.extractor import (
    get_localization_callsigns_data,
    get_listing_callsigns_data,
    get_feed_data,
    get_listing_data,
)

from resty import client
import requests

def home(request):
    return render_to_response('home.html', {})

def test(request):
    return render_to_response('test.html', {})

def station_by_zip(request):
    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        context['zipcode'] = zipcode

        #
        # http://services-qa.pbs.org/callsigns/zip/22202.json
        #
        callsign_url = settings.SODOR_ENDPOINT + 'callsigns/zip/' + zipcode + '.json'
        context = {}

        data = requests.get(callsign_url)
        if data.status_code != 200:
            return HttpResponseNotFound()

        jd = data.json
        # have to loop through and generate the summary for the page
        station_list = {}
        for callsign_map in jd['$items']:
            callsign = callsign_map['$links'][0]
            owner_station = callsign['$links'][0]

            owner_station_callsign = None
            for rel in owner_station['$links']:
                    if rel['$relationship'] == 'flagship':
                        owner_station_callsign = rel['callsign']

            print '------ found %s with flagship %s' % (owner_station_callsign,callsign['callsign'])
            # Check to see if we've seen this station before
            if owner_station_callsign in station_list:
                print 'found existing station'
                # have seen this station before so process it
                station = station_list[owner_station_callsign]
                # Check to see if we've moved up the ranking
                print 'callsign rank = %s' % callsign_map['rank']
                # Some callsigns will not have a rank and thus we should
                # add them to a low confidence list
                if not callsign_map['rank']:
                    station['loconf_callsigns'].append(callsign['callsign'])
                else:
                    if station['rank'] > callsign_map['rank']:
                        # this callsign has a lower (better) ranking so use it
                        station['rank'] = callsign_map['rank']

                    if station['confidence'] < callsign_map['confidence']:
                        # this callsign has a higher (better) confidence so use it
                        station['confidence'] = callsign_map['confidence']

                    # now add callsign to the list
                    station['callsigns'].append(callsign['callsign'])

            else:
                print 'create new station'
                # create a new station entry and add it to the stations list
                station = {}
                station['flagship'] = owner_station_callsign
                station['confidence'] = callsign_map['confidence']
                station['rank'] = callsign_map['rank']
                print 'rank = %s' % station['rank']
                station['short_common_name'] = owner_station['short_common_name']
                # get id from url
                station['id'] = _get_id_from_url(owner_station['$self'])
                station['callsigns'] = []
                station['loconf_callsigns'] = []
                if callsign_map['rank']:
                    station['callsigns'].append(callsign['callsign'])
                else:
                    station['loconf_callsigns'].append(callsign['callsign'])

                station_list[owner_station_callsign] = station

            print 'finished with station: %s' % station

        # now we can break out the two lists by confidence
        hiconf = []
        loconf = []
        for cs,station in station_list.iteritems():
            if station['confidence'] == 100:
                hiconf.append(station)
            else:
                loconf.append(station)

        # now sort both lists
        hiconf = sorted(hiconf,key=lambda k: k['rank'])
        loconf = sorted(loconf,key=lambda k: k['rank'])
        context['hiconf'] = hiconf
        context['loconf'] = loconf
        #context['station_list'] = station_list

    return render_to_response(
        'station_by_zip.html',
        context,
        context_instance=RequestContext(request)
    )

def _get_id_from_url(url):
    if not url:
        return None
    return(url[url.rfind('/')+1:-5])

def station_by_state(request):
    return render_to_response('test.html')

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

                            #import pdb; pdb.set_trace()


                            if listings_data:
                                feeds.setdefault(feed_name, []).extend(
                                    listings_data)
                    if feeds:
                        callsigns.setdefault(callsign, []).append(feeds)
                        listings.append(callsigns)
            context['listings'] = listings
            context['selected_headend'] = selected_headend
    return render_to_response(
        'zipcode_listings.html',
        context,
        context_instance=RequestContext(request)
    )


def get_headends_for_zipcode(zipcode):
    homepage = client.load(settings.SODOR_ENDPOINT)
    zipcodes = homepage.service('zipcodes')
    zipcode = zipcodes.filter('zip', zipcode=zipcode).items()[0]
    headends = zipcode.related('presence')
    return [(h.content.name, h.self) for h in headends.items()]


def get_feeds_for_headend(headend_url):
    headend = client.load(headend_url)
    result = {}
    for channel in headend.related('children').items():
        cable_number = channel.content.cable_number
        feed = channel.related('related')
        full_name = feed.related('summary').content.full_name
        callsign = feed.related('parent').content.callsign
        result[feed.self] = [cable_number, full_name, callsign]
    return result


def get_feeds_for_zipcode(zipcode):
    result = {}
    homepage = client.load(settings.SODOR_ENDPOINT)
    zipcodes = homepage.service('zipcodes')
    zipcode = zipcodes.filter('zip', zipcode=zipcode).items()[0]
    cs2zipm = zipcode.related('search')
    for cs2zip in cs2zipm.items():
        cs = cs2zip.related('related')
        callsign = cs.content.callsign
        for feed in cs.related('children').items():
            feed_url = feed.self
            ota = feed.related('summary')
            full_name = ota.content.full_name
            result[feed_url] = [full_name, callsign]
    return result


def get_episode_listings(episode_url):
    result = {}
    episode = client.load(episode_url)
    listings = episode.related('related')
    for listing in listings.items():
        feed_url = listing.related('parent').self
        result.setdefault(feed_url, []).append({
            'start_date': listing.content.start_date,
            'start_time': listing.content.start_time,
        })
    return result


def episode_listings(request):
#     current_dir = os.path.dirname(
#         os.path.normpath(os.sys.modules[settings.SETTINGS_MODULE].__file__)
#     )
#     mock_file = open(
#         os.path.join(current_dir, "consumer/fixtures/mock_ep_data.json")
#     )
#    data = json.loads(mock_file.read())
#    mock_listings = data['mock_listings']
#     mock_headends = data['mock_headends']

    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        episode_url = request.POST.get('episode_url')
        headend_url = request.POST.get('channels_url')

        context['zipcode'] = zipcode
        context['episode_url'] = episode_url
        context['selected_channels_url'] = headend_url

        context['headends'] = get_headends_for_zipcode(zipcode)
        context['episode_title'] = client.load(episode_url).content.title

        if headend_url:
            headend_feeds = get_feeds_for_headend(headend_url)
            all_listings = get_episode_listings(episode_url)

            common_feeds = set(headend_feeds.keys()) & set(all_listings.keys())

            d = {}
            for feed_url in common_feeds:
                l = d.setdefault(headend_feeds[feed_url][2], [])
                l.append({
                    headend_feeds[feed_url][1]:
                    [headend_feeds[feed_url][0]] + all_listings[feed_url]
                })

            context['listings'] = [
                {cs: the_rest} for cs, the_rest in d.items()
            ]
        else:
            ota_feeds = get_feeds_for_zipcode(zipcode)
            all_listings = get_episode_listings(episode_url)

            common_feeds = set(ota_feeds.keys()) & set(all_listings.keys())

            d = {}
            for feed_url in common_feeds:
                l = d.setdefault(ota_feeds[feed_url][1], [])
                l.append({
                    ota_feeds[feed_url][0]: all_listings[feed_url]
                })

            context['listings'] = [
                {cs: the_rest} for cs, the_rest in d.items()
            ]

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



def view_station(request,station_id):

    station_url = settings.SODOR_ENDPOINT + 'station/' + str(int(station_id)) + '.json'
    context = {}
    try:
        station_data = client.load(station_url)
    except KeyError:
        return HttpResponseNotFound('Station not found')

    context['station'] = station_data.content

    flagship = station_data.related('flagship')
    context['callsign'] = flagship.content.callsign
    primary_feeds = flagship.related('children')
    feeds = []
    for f in primary_feeds.items():
        f_url = f.self
        f_id = f_url[f_url.rfind('/')+1:-5]
        feed_obj = {}
        feed_obj['id'] = f_id
        otc = f.related('summary').content
        feed_obj['otc'] = otc
        feeds.append(feed_obj)
    context['feeds'] = feeds

    # http://services-qa.pbs.org/tvss/today/wmpb/
    whats_on_today_url = settings.SODOR_ENDPOINT + 'tvss/today/' + flagship.content.callsign

    data = requests.get(whats_on_today_url)
    if data.status_code == 200:
        jd = data.json
        # have to loop through and covert the goofy timestamps into datetime objects
        for f in jd['feeds']:
            for l in f['listings']:
                l['start_time_obj'] = datetime.datetime.strptime(l['start_time'], "%H%M")
        context['listings_today'] = jd

    return render_to_response(
        'view_station.html',
        context,
        context_instance=RequestContext(request)
    )



