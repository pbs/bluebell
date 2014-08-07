import os
import re
import json
import urllib
import datetime
from django.conf import settings
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseNotFound
from dateutil import parser

from resty import client
import requests

def home(request):
    context = {}
    context['remote_addr'] = request.META.get('REMOTE_ADDR')
    return render_to_response('home.html', context,
        context_instance=RequestContext(request))

def test(request):
    return render_to_response('test.html', {})

def station_by_zip(request,zip=None):
    context = {}
    if request.method == 'POST' or zip:
        if zip:
            zipcode = zip
        else:
            zipcode = request.POST.get('zipcode')
        context['zipcode'] = zipcode

        #
        # http://services-qa.pbs.org/callsigns/zip/22202.json
        #
        callsign_url = settings.SODOR_ENDPOINT + 'callsigns/zip/' + zipcode + '.json'

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

    # Get list of states
    # http://services-qa.pbs.org/states.json/

    list_of_states_url = settings.SODOR_ENDPOINT + 'states.json'
    context = {}

    data = requests.get(list_of_states_url)
    if data.status_code == 200:
        context['states'] = data.json['$items']

    return render_to_response(
        'station_by_state.html',
        context,
        context_instance=RequestContext(request)
    )

def station_state(request,state):

    # Get list of stations in a state
    # http://services-qa.pbs.org/stations/state/AL.json

    list_of_stations_url = settings.SODOR_ENDPOINT + 'stations/state/' + state + '.json'
    context = {}

    data = requests.get(list_of_stations_url)
    if data.status_code == 200:
        jd = data.json['$items']
        station_list = []
        for s in jd:
            station = {}
            station['name'] = s['$links'][0]['common_name']
            station['id'] = _get_id_from_url(s['$links'][0]['$self'])
            station['city'] = s['$links'][0]['mailing_city']
            station['state'] = s['$links'][0]['mailing_state']
            station['short_name'] = s['$links'][0]['short_common_name']
            for cs in s['$links'][0]['$links']:
                if cs['$relationship'] == 'flagship':
                    station['flagship_callsign'] = cs['callsign']
            station_list.append(station)

        context['station_list'] = station_list

    context['statex'] = state
    return render_to_response(
        'station_by_state2.html',
        context,
        context_instance=RequestContext(request)
    )

def station_by_ip(request, ip):

    # Get zip for this ip
    # http://services-qa.pbs.org/zipcodes/ip/138.88.141.44.json

    list_of_zips_url = settings.SODOR_ENDPOINT + 'zipcodes/ip/' + ip + '.json'
    context = {}
    zipcode = None
    print list_of_zips_url
    data = requests.get(list_of_zips_url)
    if data.status_code == 200:
        print data.json
        zipcode = data.json['$items'][0]['zipcode']

    if not zipcode:
        return HttpResponseNotFound()

    return redirect('station_by_zip', zip=zipcode)

def station_by_geo(request):

    return redirect(HttpResponse("good"))

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

    #
    # Get today's listings
    # http://services-qa.pbs.org/tvss/today/wmpb/
    #
    whats_on_today_url = settings.SODOR_ENDPOINT + 'tvss/' + flagship.content.callsign + '/today/'

    data = requests.get(whats_on_today_url, headers={'X-PBSAUTH': settings.TVSS_KEY})
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



