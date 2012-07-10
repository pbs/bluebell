def get_callsigns_data(callsign_by_zip_data, zipcode):
    context = {}
    result = {}
    stations_merged_data = {}
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

    seen = set()
    ztc_data_keys = [seen.add(item.keys()[0]) or item.keys()[0]
        for item in ztc_data if item.keys()[0] not in seen
    ]

    ordered_ztc_data = [result.get(item) for item in ztc_data_keys]
    context['ztc_data'] = ordered_ztc_data

    return context
