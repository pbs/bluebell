import urllib
import json
from urlparse import urljoin

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
        callsign_by_zip = settings.SODOR_CALLSIGN_BY_ZIP % zipcode
        url = urljoin(sodor_base_url, callsign_by_zip)
        data = json.loads(urllib.urlopen(url).read())
        for item in data['$items']:
            callsigns.append({
                'callsign': item['$links'][0]['callsign'],
                'short_common_name':
                    item['$links'][0]['$links'][0]['short_common_name'],
                'flagship':
                    item['$links'][0]['$links'][0]['$links'][1]['callsign'],
                'rank': item['rank'],
                'confidence': item['confidence']}
        )
        context['data'] = callsigns
    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def show_listings(request):
    return render_to_response('show_listings.html', {})
