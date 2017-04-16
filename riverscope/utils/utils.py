import requests
import time
import urllib


EA_API_ROOT = 'https://environment.data.gov.uk/flood-monitoring'
QUALIFIERS = ('Stage', 'Downstream Stage', 'Groundwater', 'Tidal Level')
STATUSES = ('Active', 'Closed', 'Suspended')
PARAMETERS = ('level', 'flow')
PARAMETER_NAMES = ('Water Level', 'Flow')
STATION_TYPES = ('SingleLevel', 'MultiTraceLevel', 'Coastal', 'Groundwater', 'Meteorological')


class ParameterError(Exception):
    pass


def stations_url(rloiid=None, search=None, qualifier=None, status=None,
    label=None, town=None, catchment_name=None, river_name=None, parameter=None,
    parameter_name=None, lat_long_dist=None, station_ref=None, stn_type=None,
    limit=None):
    """Get stations matching the filter arguments passed. Returns a url.

    rloiid
        Return only the station (if there is one) whose RLOIid (River Levels
        on the Internet identifier) matches `rloiid`.
    search
        Return only those stations whose label contains `search`
    qualifier
        Return only those stations which measure parameters with qualifier
        `qualifier`. Useful qualifiers are Stage and Downstream Stage (for
        stations such as weirs which measure levels at two locations),
        Groundwater for groundwater levels as opposed to river levels and Tidal
        Level for tidal levels.
    status
        Return only those stations with the given status, where `status` can be
        one of 'Active', 'Closed' or 'Suspended'
    label
        Return only those stations whose label is exactly `label` and is case
        sensitive.
    town
        Return only those stations whose town is `town`. Not all stations have
        an associated town.
    catchment_name
        Return only those stations whose catchment name is exactly
        `catchment_name`. Not all stations have an associated catchment area.
    river_name
        Return only those stations whose river name is exactly `river_name`.
        Not all stations have an associated river name.
    parameter
        Return only those stations which measure parameters with the given
        short form name `parameter`, for example 'level' or 'flow'.
    parameter_name
        Return only those stations which measure parameters with the given name
        `parameter_name`, for example 'Water Level' or 'Flow'.
    lat_long_dist
        return those stations whose location falls within `dist` km of the
        given lat/long (in WGS84 coordinates), this may be approximated by a
        bounding box.
    station_ref
        Return only those stations whose reference identifier is
        `station_ref`. The station reference is an internal identifier
        used by the Environment Agency.
    stn_type
        Return only those stations of the given type, where `stn_type` can be
        one of 'SingleLevel', 'MultiTraceLevel', 'Coastal', 'Groundwater' or
        'Meteorological'
    limit
        Return `limit` number of matching stations. If omitted, limit is set to
        500, with a hard limit of 10000.
    """
    if qualifier and qualifier not in QUALIFIERS:
        raise ParameterError(
            'qualifier must be one of ({})'.format(', '.join(QUALIFIERS)))
    if status and status not in STATUSES:
        raise ParameterError(
            'status must be one of ({})'.format(', '.join(STATUSES)))
    if parameter and parameter not in PARAMETERS:
        raise ParameterError(
            'parameter must be one of ({})'.format(', '.join(PARAMETERS)))
    if parameter_name and parameter_name not in PARAMETER_NAMES:
        raise ParameterError(
            'parameter_name must be one of ({})'.format(', '.join(PARAMETER_NAMES)))
    if stn_type and stn_type not in STATION_TYPES:
        raise ParameterError(
            'stn_type must be one of ({})'.format(', '.join(STATION_TYPES)))
    if lat_long_dist:
        if (not all(lat_long_dist) or
            len(lat_long_dist) != 3 or
            not all([isinstance(i, (float, int)) for i in lat_long_dist])):
            raise ParameterError(
                'lat_long_dist must contain 3 numbers')

    stations_token = '/id/stations'

    tokens = (
        'parameterName={}'.format(parameter_name) if parameter_name else None,
        'parameter={}'.format(parameter) if parameter else None,
        'qualifier={}'.format(qualifier) if qualifier else None,
        'label={}'.format(label) if label else None,
        'town={}'.format(town) if town else None,
        'catchmentName={}'.format(catchment_name) if catchment_name else None,
        'riverName={}'.format(river_name) if river_name else None,
        'stationReference={}'.format(station_ref) if station_ref else None,
        'RLOIid={}'.format(rloiid) if rloiid else None,
        'search={}'.format(search) if search else None,
        'lat={}&long={}&dist={}'.format(*lat_long_dist) if lat_long_dist else None,
        'type={}'.format(stn_type) if stn_type else None,
        'status={}'.format(status) if status else None,
        '_limit={}'.format(limit) if limit else None)

    filter_tokens = '&'.join(filter(None, tokens))

    safe_url_tokens = urllib.parse.quote(filter_tokens, safe="&$,+/:;=?@#")
    return EA_API_ROOT + stations_token + '?' + safe_url_tokens


def get_url_json_response(url):
    return requests.get(url).json()


def get_river_stations(with_typical_range=False):
    """Create a generator returning a tuple of notation, station_dict for each
    station returned by the EA stations API call.

    args:
        with_typical_range: If true, also collects the typical min/max
            levels of the station. Warning, this is a much more lengthy query
            as it makes a request per station (~1800).
    """
    stn_url = stations_url(parameter='level', qualifier='Stage', limit=10000)
    stations = get_url_json_response(stn_url)

    for station in stations['items']:
        if not all((station.get('lat') , station.get('long'))):
            continue
        url = station.get('@id')
        river_name = station.get('riverName')
        town = station.get('town')
        label = station.get('label')
        stage_scale_url = station.get('stageScale')
        notation = station['notation']
        try:
            lat = float(station['lat'])
            lon = float(station['long'])
        except TypeError:
            continue

        stage_scale = None
        typical_low = None
        typical_high = None

        if with_typical_range and stage_scale_url:
            try:
                # Not all stations have a stageScale
                stage_scale = get_url_json_response(station['stageScale'])
            except KeyError:
                pass

            if stage_scale:
                typical_low = stage_scale['items']['typicalRangeLow']
                typical_high = stage_scale['items']['typicalRangeHigh']

        station_dict = {'town': town, 'river_name': river_name, 'label': label,
                        'lat': lat, 'lon': lon, 'stage_scale_url': stage_scale_url,
                        'typical_low': typical_low , 'typical_high': typical_high,
                        'url': url, 'latest': None, 'penultimate': None}

        yield notation, station_dict


def start_timer():
    return time.time()


def end_timer(start_time, human_readable=True):
    elapsed_time = int(time.time() - start_time)
    if human_readable:
        m, s = divmod(elapsed_time, 60)
        h, m = divmod(m, 60)
        out_time = "{}h {}m {}s".format(round(h), round(m), round(s))
    else:
        out_time = elapsed_time

    return out_time