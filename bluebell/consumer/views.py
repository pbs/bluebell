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
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        callsign_by_zip = settings.SODOR_CALLSIGN_BY_ZIP % zipcode
        url = urljoin(sodor_base_url, callsign_by_zip)
        data = json.loads(urllib.urlopen(url).read())
        context['data'] = data
    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def show_listings(request):
    return render_to_response('show_listings.html', {})
