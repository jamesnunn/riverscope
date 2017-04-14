import pytest

from riverscope.utils import utils

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

def test_get_url_response_something():
    url = utils.stations_url(station_ref='E8360')
    resp = utils.get_url_json_response(url)['items'][0]['label']
    assert resp == 'Uckfield Mill upstream'

def test_get_url_response_nothing():
    url = utils.stations_url(station_ref='E8360', search='blah')
    resp = utils.get_url_json_response(url)['items']
    assert resp == []