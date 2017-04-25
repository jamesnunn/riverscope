import json

from django.shortcuts import render
from django.shortcuts import render_to_response
from django.db import connection
from django.core.serializers import serialize

from stations.models import Stations


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def get_station_readings():
    with connection.cursor() as cursor:
        cursor.execute(('select '
                            's.station_ref, '
                            's.label, '
                            's.town, '
                            's.river_name, '
                            's.rloiid, '
                            's.url, '
                            's.typical_low, '
                            's.typical_high, '
                            'st_x(s.point) as lon, '
                            'st_y(s.point) as lat, '
                            # Needs to return datetime and order by
                            'array_agg(r.measure) as measures '
                        'from stations_stations s '
                        'left join stations_stationreadings r on s.id = r.station_id '
                        'group by '
                            's.station_ref,'
                            's.label, '
                            's.town, '
                            's.river_name, '
                            's.rloiid, '
                            's.url, '
                            's.typical_low, '
                            's.typical_high,'
                            'lat,'
                            'lon'))
        return dictfetchall(cursor)

def station_readings_to_geojson(data):
    geojson = {
    'type': 'FeatureCollection',
    'features': [
    {
        'type': 'Feature',
        'geometry' : {
            'type': 'Point',
            'coordinates': [d['lon'], d['lat']],
            },
        'properties' : d,
        } for d in data]
    }
    return geojson


def index(request):

    station_readings = station_readings_to_geojson(get_station_readings())
    return render_to_response('index.html', {'stations': json.dumps(station_readings)})
