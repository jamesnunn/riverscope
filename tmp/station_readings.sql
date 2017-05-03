drop view station_datetime_readings;
create or replace view station_datetime_readings as
select
s.station_ref,
s.label,
s.town,
s.river_name,
s.rloiid,
s.url,
s.typical_low,
s.typical_high,
st_x(s.point) as lon,
st_y(s.point) as lat,
array_agg(r.datetime::text order by r.datetime asc) as measure_datetimes,
array_agg(r.measure order by r.datetime asc) as measures
from stations_stations s
left join stations_stationreadings r on s.id = r.station_id
group by
s.station_ref,
s.label,
s.town,
s.river_name,
s.rloiid,
s.url,
s.typical_low,
s.typical_high,
lat,
lon;