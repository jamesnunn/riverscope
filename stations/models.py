from django.contrib.gis.db import models as models


class Stations(models.Model):
    station_ref = models.CharField(max_length=50)
    rloiid = models.IntegerField()
    url = models.CharField(max_length=150)
    town = models.CharField(max_length=100)
    river_name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    lat = models.FloatField()
    lon = models.FloatField()
    stage_scale_url = models.CharField(max_length=150)
    typical_low = models.FloatField()
    typical_high = models.FloatField()
    point = models.PointField(default=None)

    def __str__(self):
        return self.url