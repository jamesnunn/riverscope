from collections import namedtuple
import datetime
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


def get_url_json_response(url):
    return requests.get(url).json()


Station = namedtuple('Station', 'station_ref rloiid url town river_name '
                     'label stage_scale_url typical_low typical_high '
                     'measure_url point')


def build_ea_station_url(func):
    def wrapper(*args, **kwargs):
        url_elements, tokens = func(*args, **kwargs)

        url_elements = list(filter(None, url_elements)) if url_elements else None
        url_token = '/'.join(url_elements) if url_elements else ''
        filter_tokens = '&'.join(filter(None, tokens))
        if filter_tokens:
            safe_filter_tokens = '?' + urllib.parse.quote(filter_tokens, safe="&$,+/:;=?@#")
        else:
            safe_filter_tokens = ''
        return EA_API_ROOT + '/' + url_token + safe_filter_tokens
    return wrapper


@build_ea_station_url
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

    return (('id', 'stations'), tokens)


def get_river_stations(with_typical_range=False, **kwargs):
    """Create a generator returning a Station object for each station found.

    kwargs:
        with_typical_range: If true, also collects the typical min/max
            levels of the station. Warning, this is a much more lengthy query
            as it makes a request per station (~1800).
        All other kwargs are passed to stations_url function call.

    """
    stn_url = stations_url(**kwargs)
    stations = get_url_json_response(stn_url)

    for station in stations['items']:
        if not all((station.get('lat') , station.get('long'))):
            continue
        url = station.get('@id')
        river_name = station.get('riverName')
        town = station.get('town')
        label = station.get('label')
        stage_scale_url = station.get('stageScale')
        station_ref = station['notation']
        rloiid = station.get('RLOIid')
        rloiid = int(rloiid) if rloiid else None
        measure = station.get('measures')
        if measure:
            measure = measure[0]['@id'].split('/')[-1]
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
                # TODO Multithread this
                stage_scale = get_url_json_response(station['stageScale'])
            except KeyError:
                pass

            if stage_scale:
                try:
                    typical_low = float(stage_scale['items']['typicalRangeLow'])
                    typical_high = float(stage_scale['items']['typicalRangeHigh'])
                except KeyError:
                    pass

        station = Station(station_ref, rloiid, url, town, river_name, label,
                         stage_scale_url, typical_low, typical_high, measure,
                         (lon, lat))

        yield station


@build_ea_station_url
def readings_url(latest=False, today=False, date=None, since=None, limit=None,
                 date_range=None, parameter=None, qualifier=None, sort=False,
                 station_ref=None, measure=None):
    """Get readings matching the filter arguments passed. Returns a url.

        latest: bool
            Return only the most recently available reading for each included
            measure.

        today: bool
            Return all the readings taken today for each included measure.

        date: datetime.datetime:
            Return all the readings taken on the specified day for each
            included measure.

        date_range: (datetime.datetime, datetime.datetime)
            Return the readings taken on the specified range of days for each
            included measure, up to the specified `limit`. If no `limit` is
            given then a default limit of 500 will be used.

        since: datetime.datetime
            Return the readings taken since the given date time (not
            inclusive), up to the specified _limit. If no _limit is given then
            a default limit of 500 will be used. Typically when tracking a
            particular measurement then use the dateTime of the last retrieved
            value as the since parameter to find any new readings. Will accept
            a simple date value such as 2016-09-07 which will be interpreted as
            2016-09-07T:00:00:00Z.

        parameter
            Return only readings for measures of parameters with the given
            short form name x, for example level or flow.

        qualifier
            Return only readings of measures with qualifier x. Useful
            qualifiers are Stage and Downstream Stage (for stations such as
            weirs which measure levels at two locations), Groundwater for
            groundwater levels as opposed to river levels and Tidal Level for
            tidal levels.

        limit
            Limits the number of results to `limit`. If used in conjuction with
            `sorted=True`, will return the latest `limit` readings.

        sort
            Order the array of returned readings into descending order by date,
            this done before the limits is applied thus enabling you to fetch
            the most recent n readings.

        measure
            Get readings from this measure url.
    """
    if qualifier and qualifier not in QUALIFIERS:
        raise ParameterError(
            'qualifier must be one of ({})'.format(', '.join(QUALIFIERS)))
    if parameter and parameter not in PARAMETERS:
        raise ParameterError(
            'parameter must be one of ({})'.format(', '.join(PARAMETERS)))
    if date_range:
        if date_range[0] > date_range[1]:
            raise ParameterError('Dates must be ordered earliest to latest.')
    if station_ref and measure:
        raise ParameterError('Only one of station_ref or measure is allowed.')

    date_fmt = '%Y-%m-%d'

    tokens = (
        'latest' if latest else None,
        'today' if today else None,
        'date={}'.format(date.strftime(date_fmt)) if date else None,
        'startdate={}&enddate={}'.format(
            *map(lambda x: x.strftime(date_fmt), date_range)) if date_range else None,
        'since={}'.format(since.strftime(date_fmt)) if since else None,
        'parameter={}'.format(parameter) if parameter else None,
        'qualifier={}'.format(qualifier) if qualifier else None,
        '_limit={}'.format(limit) if limit else None,
        '_sorted' if sort else None
        )

    if not station_ref and not measure:
        url_tokens = ('data', 'readings')
    elif station_ref:
        url_tokens = ('id', 'stations', station_ref, 'readings')
    elif measure:
        url_tokens = ('id', 'measures', measure, 'readings')

    return url_tokens, tokens
