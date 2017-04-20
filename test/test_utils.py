import pytest
import datetime

from stations.management.commands import utils

def test_stations_url_tokenising():
    url = utils.stations_url(rloiid='lor em', search='Ips!"£$%^&*()_+{}:;@\'~#<>?,./|\¬`um',
        qualifier='Downstream Stage', status='Active', label='consectetur',
        town='adipiscing', catchment_name='vitae', river_name='amet',
        parameter='level', parameter_name='Water Level', lat_long_dist=(-1.23123, 2.231, 50.6),
        station_ref='aSD', stn_type='Groundwater', limit=10)

    exp_url = ('https://environment.data.gov.uk/flood-monitoring/id/stations?'
        'parameterName=Water%20Level&parameter=level&qualifier=Downstream%20Stage&'
        'label=consectetur&town=adipiscing&catchmentName=vitae&riverName=amet&'
        'stationReference=aSD&RLOIid=lor%20em&search=Ips%21%22%C2%A3$%25%5E&%2A%28%29_+'
        '%7B%7D:;@%27%7E#%3C%3E?,./%7C%5C%C2%AC%60um&lat=-1.23123&long=2.231&'
        'dist=50.6&type=Groundwater&status=Active&_limit=10')
    assert url == exp_url

def test_stations_url_tokenise_lat_long_dist():
    url = utils.stations_url(lat_long_dist=(-1.23123, 2.231, 50.6))
    exp_url = ('https://environment.data.gov.uk/flood-monitoring/id/stations?'
               'lat=-1.23123&long=2.231&dist=50.6')
    assert url == exp_url

def test_stations_url_lat_long_dist_raises_with_string():
    with pytest.raises(utils.ParameterError):
        utils.stations_url(lat_long_dist='bla')

def test_stations_url_lat_long_dist_raises_with_list():
    with pytest.raises(utils.ParameterError):
        utils.stations_url(lat_long_dist=['1', 2, 3])

def test_stations_url_lat_long_dist_raises_with_ints():
    utils.stations_url(lat_long_dist=[1, 2, 3])

def test_stations_url_raises():
    with pytest.raises(utils.ParameterError):
        utils.stations_url(status='blah')

def test_get_river_stations_something():
    stns = list(utils.get_river_stations(station_ref='E8360'))
    label = stns[0].label
    assert label == 'Uckfield Mill upstream'

def test_get_river_stations_nothing():
    stns = list(utils.get_river_stations(station_ref='E8360', search='blah'))
    assert stns == []

def test_readings_url_tokenising():
    url = utils.readings_url(latest=True, today=True,
        date=datetime.date(2015, 5, 18), since=datetime.date(2015, 5, 18),
        limit=10, date_range=(datetime.date(2015, 5, 18), datetime.date(2015, 5, 29)),
        parameter='level', qualifier='Stage', sorted=True, station_ref='blah')

    exp_url = ('https://environment.data.gov.uk/flood-monitoring/id/stations/'
        'blah/readings?latest&today&date=2015-05-18&startdate=2015-05-18&'
        'enddate=2015-05-29&since=2015-05-18&parameter=level&qualifier=Stage'
        '&_limit=10&_sorted')
    assert url == exp_url