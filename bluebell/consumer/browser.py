import re
import urllib
import json


def navigate_to_callsigns(sodor_entry_point, zipcode):
    services_data = _read_data(sodor_entry_point)
    zipcode_collection_url = (
        services_data['$services']['zipcodes']['$filters']['zip']
    )
    zipcode_collection_url = (
        re.sub('{zipcode}', zipcode, zipcode_collection_url)
    )
    zipcode_collection_data = _read_data(zipcode_collection_url)

    if (not zipcode_collection_data or
        zipcode_collection_data['$items'] == []):
        return

    callsign_by_zip_url = (
        zipcode_collection_data['$items'][0]['$links'][0]['$self']
    )
    return  _read_data(callsign_by_zip_url)


def navigate_to_listings(sodor_entry_point, zipcode):
    pass


def _read_data(url):
    try:
        response = json.loads(urllib.urlopen(url).read())
    except ValueError:
        return None
    else:
        return response
