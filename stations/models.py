from django.contrib.gis.db import models as models


class Stations(models.Model):
    station_ref = models.CharField(max_length=50, unique=True)
    rloiid = models.IntegerField(null=True)
    url = models.CharField(max_length=150)
    town = models.CharField(max_length=100, null=True)
    river_name = models.CharField(max_length=50, null=True)
    label = models.CharField(max_length=100, null=True)
    stage_scale_url = models.CharField(max_length=150, null=True)
    typical_low = models.FloatField(null=True)
    typical_high = models.FloatField(null=True)
    point = models.PointField(default=None)

    def __str__(self):
        return station_ref