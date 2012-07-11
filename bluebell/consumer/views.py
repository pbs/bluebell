from django.conf import settings
from django.shortcuts import render_to_response
from django.template import RequestContext

from bluebell.consumer.browser import (
    navigate_to_callsigns, navigate_to_listings
)
from bluebell.consumer.extractor import (
    get_callsigns_data, get_listings_data
)


def home(request):
    return render_to_response('home.html', {})


def localize_stations(request):
    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        callsigns_page = navigate_to_callsigns(
            settings.SODOR_ENDPOINT, zipcode
        )
        context = get_callsigns_data(callsigns_page, zipcode)

    return render_to_response(
        'localize_stations.html',
        context,
        context_instance=RequestContext(request)
    )


def show_listings(request):
    context = {}
    if request.method == 'POST':
        zipcode = request.POST.get('zipcode')
        listings_page = navigate_to_listings(
            settings.SODOR_ENDPOINT, zipcode
        )
        context = get_listings_data(listings_page, zipcode)

    return render_to_response(
        'show_listings.html',
        context,
        context_instance=RequestContext(request)
    )
