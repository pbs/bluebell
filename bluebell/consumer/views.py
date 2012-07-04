from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from bluebell.consumer.extractors import extract_callsign_by_zip


def home(request):
    return render_to_response('home.html', {})


def localize_stations(request):
    context = {}
    if request.method == 'POST':
        sodor_base_url = settings.SODOR_ENDPOINT
        zipcode = request.POST.get('zipcode')
        context = extract_callsign_by_zip(sodor_base_url, zipcode)

    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def show_listings(request):
    return render_to_response('show_listings.html', {})
