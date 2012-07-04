import re
import urllib
import json


def extract_callsign_by_zip(sodor_entry_point, zipcode):
        context = {}
        callsigns = []

        context['zipcode'] = zipcode

        services_data = _read_data(sodor_entry_point)
        zipcode_collection_url = (
            services_data['$services']['zipcodes']['$filters']['zip']
        )
        zipcode_collection_url = (
            re.sub('{zipcode}', zipcode, zipcode_collection_url)
        )
        zipcode_collection_data = _read_data(zipcode_collection_url)

        if zipcode_collection_data['$items'] == []:
            return context

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
        context['data'] = callsigns

        return context


def _read_data(url):
    return json.loads(urllib.urlopen(url).read())
