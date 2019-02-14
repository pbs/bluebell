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
import requests
from django.views.decorators.csrf import csrf_exempt

def listings(request,callsign,target_date=None):

    if not target_date:
        target_date = datetime.datetime.now().strftime("%Y%m%d")

    # Get listings for a particular date
    # http://services-qa.pbs.org/tvss/weta/day/20121002/
    #
    listings_url = settings.SODOR_ENDPOINT + 'tvss/' + callsign + '/day/' + target_date + '/'
    context = {}

    data = requests.get(listings_url, headers={'X-PBSAUTH': settings.TVSS_KEY})
    if data.status_code == 200:
        jd = data.json()
        # have to loop through and covert the goofy timestamps into datetime objects
        for f in jd['feeds']:
            # check the first listing in the list.  if it doesn't start at midnight
            # then we have to add padding
            first_time = f['listings'][0]['start_time']
            if first_time != '0000':
                time_delta_min = int(first_time[:2]) * 60 + int(first_time[2:])
                dummy = {}
                dummy['title'] = ""
                dummy['start_time'] = '0000'
                dummy['minutes'] = time_delta_min
                f['listings'].insert(0,dummy)
            for l in f['listings']:
                l['start_time_obj'] = datetime.datetime.strptime(l['start_time'], "%H%M")
                d,rem = divmod(int(l['minutes']),30)
                if 1 > d:
                    d = 1
                l['colspan'] = d
        context['listings'] = jd

    context['callsign'] = callsign

    return render_to_response(
        'feed_listings.html',
        context,
        context_instance=RequestContext(request)
    )

def view_program(request, program_id, callsign):
    #
    # Get listings for a particular program
    # http://services-qa.pbs.org/tvss/weta/upcoming/program/752
    #
    program_url = settings.SODOR_ENDPOINT + 'tvss/' + callsign +'/upcoming/program/' + str(int(program_id)) + '/'
    context = {}

    data = requests.get(program_url, headers={'X-PBSAUTH': settings.TVSS_KEY})
    if data.status_code == 200:
        jd = data.json()
        # have to loop through and covert the goofy timestamps into datetime objects
        for l in jd['upcoming_episodes']:
            l['day_obj'] = parser.parse(l['day'])
            l['start_time_obj'] = datetime.datetime.strptime(l['start_time'], "%H%M")
        context['program'] = jd

    context['callsign'] = callsign

    return render_to_response(
        'view_program.html',
        context,
        context_instance=RequestContext(request)
    )

def view_show(request, show_id, callsign):
    #
    # Get listings for a particular show
    # http://services-qa.pbs.org/tvss/weta/upcoming/show/episode_9509/
    #
    show_url = settings.SODOR_ENDPOINT + 'tvss/'+ callsign + '/upcoming/show/' + show_id + '/'
    context = {}

    data = requests.get(show_url, headers={'X-PBSAUTH': settings.TVSS_KEY})
    if data.status_code == 200:
        jd = data.json()
        # have to loop through and covert the goofy timestamps into datetime objects
        for l in jd['upcoming_shows']:
            l['day_obj'] = parser.parse(l['day'])
            l['start_time_obj'] = datetime.datetime.strptime(l['start_time'], "%H%M")
        context['show'] = jd

    context['callsign'] = callsign

    return render_to_response(
        'view_show.html',
        context,
        context_instance=RequestContext(request)
    )

@csrf_exempt
def search(request, callsign):

    #
    # Search listings for a callsign
    # http://services-qa.pbs.org/tvss/<callsign>/search/<term>/
    #
    searchterm = request.GET.get('q')

    context = {}
    context['callsign'] = callsign
    context['searchterm'] = searchterm

    if searchterm:
        search_url = settings.SODOR_ENDPOINT + 'tvss/' + callsign + '/search/' + urllib.quote(searchterm)

        data = requests.get(search_url, headers={'X-PBSAUTH': settings.TVSS_KEY})
        if data.status_code != 200:
            return HttpResponseNotFound("Could not connect to server")
        context['search_results'] = data.json()

    return render_to_response(
        'search.html',
        context,
        context_instance=RequestContext(request)
    )


