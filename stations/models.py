from django.contrib.gis.db import models as models


class Stations(models.Model)
    station_ref = models.Charfield()
    rloiid = models.Charfield()
    url = models.Charfield()
    town = models.Charfield()
    river_name = models.Charfield()
    label = models.Charfield()
    lat = models.Floatfield()
    lon = models.Floatfield()
    stage_scale_url = models.Charfield()
    typical_low = models.Floatfield()
    typical_high = models.Floatfield()
