def get_callsigns_data(callsign_by_zip_data, zipcode):
    context = {}
    ztc_data = []

    context['zipcode'] = zipcode

    if not callsign_by_zip_data:
        return context

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

    context['ztc_data'] = _group_callsign_data(ztc_data)

    return context


def _group_callsign_data(ztc_data):
    stations = {}
    stations_merged_data = {}
    for ztc in ztc_data:
        for s_common_name, station_data in ztc.iteritems():
            if s_common_name not in stations:
                stations_merged_data = {}
            else:
                stations_merged_data = stations[s_common_name]
            for key in station_data:
                stations_merged_data.setdefault(
                    key, []).append(station_data[key]
                )
                stations[s_common_name] = stations_merged_data
    unique_scn = set()
    ztc_data_keys = [unique_scn.add(item.keys()[0]) or item.keys()[0]
        for item in ztc_data if item.keys()[0] not in unique_scn
    ]
    return [stations.get(item) for item in ztc_data_keys]

