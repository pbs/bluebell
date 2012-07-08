import re
import urllib
import json


def extract_callsign_by_zip(sodor_entry_point, zipcode):
        context = {}
        result = {}
        stations_merged_data = {}
        ztc_data = []
        ordered_ztc_data = []

        context['zipcode'] = zipcode

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
            return context

        callsign_by_zip_url = (
            zipcode_collection_data['$items'][0]['$links'][0]['$self']
        )
        callsign_by_zip_data = _read_data(callsign_by_zip_url)

        for item in callsign_by_zip_data['$items']:
            scn = item['$links'][0]['$links'][0]['short_common_name']
            ztc_data.append({scn: {
                'short_common_name': scn,
                'flagship':
                    item['$links'][0]['$links'][0]['$links'][1]['callsign'],
                'confidence': item['confidence'],
                'rank': item['rank'],
                'callsign': item['$links'][0]['callsign']}
        })

        for ztc in ztc_data:
            for scn, station_data in ztc.iteritems():
                if scn not in result:
                    stations_merged_data = {}
                else:
                    stations_merged_data = result[scn]
                for key in station_data:
                    stations_merged_data.setdefault(
                        key, []).append(station_data[key]
                    )
                    result[scn] = stations_merged_data

        ordered_ztc_data = [result.get(item.keys()[0]) for item in ztc_data]
        context['ztc_data'] = ordered_ztc_data

        return context


def _read_data(url):
    try:
        response = json.loads(urllib.urlopen(url).read())
    except ValueError:
        return None
    else:
        return response
