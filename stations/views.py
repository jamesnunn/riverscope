import datetime
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
        cursor.execute('select * from station_datetime_readings;')
        return dictfetchall(cursor)


def fmt_datetime_in_dict(indictlist):
    outdictlist = []
    for d in indictlist:
        dtlist = d.get('measure_datetimes')
        if dtlist:
            outdtlist = []
            for dt in dtlist:
                if dt:
                    newd = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S+00').strftime('%H:%M %a %w %b')
                    outdtlist.append(newd)
            d['measure_datetimes'] = outdtlist
        outdictlist.append(d)
    return outdictlist


def station_readings_to_geojson(data):
    newdata = fmt_datetime_in_dict(data)
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
        } for d in newdata]
    }
    return geojson


def index(request):

    station_readings = station_readings_to_geojson(get_station_readings())
    return render_to_response('index.html', {'stations': json.dumps(station_readings)})
