import re
import urllib
import json

from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext


def home(request):
    return render_to_response('home.html', {})


def localize_stations(request):
    sodor_base_url = settings.SODOR_ENDPOINT
    context = {}
    callsigns = []

    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')

        services_data = _read_data(sodor_base_url)
        zipcode_collection_url = (
            services_data['$services']['zipcodes']['$filters']['zip']
        )
        zipcode_collection_url = (
            re.sub('{zipcode}', zipcode, zipcode_collection_url)
        )
        zipcode_collection_data = _read_data(zipcode_collection_url)

        callsign_by_zip_url = (
            zipcode_collection_data['$items'][0]['$links'][0]['$self']
        )
        callsign_by_zip_data = _read_data(callsign_by_zip_url)

        for item in callsign_by_zip_data['$items']:
            callsigns.append({
                'callsign': item['$links'][0]['callsign'],
                'short_common_name':
                    item['$links'][0]['$links'][0]['short_common_name'],
                'flagship':
                    item['$links'][0]['$links'][0]['$links'][1]['callsign'],
                'rank': item['rank'],
                'confidence': item['confidence']}
        )
        context['zipcode'] = zipcode
        context['data'] = callsigns

    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def _read_data(url):
    return json.loads(urllib.urlopen(url).read())


def show_listings(request):
    return render_to_response('show_listings.html', {})
