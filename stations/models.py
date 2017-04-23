from django.contrib.gis.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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
    measure = models.CharField(max_length=150)
    point = models.PointField(default=None)

    def __str__(self):
        return self.station_ref


class Units(models.Model):
    unit = models.CharField(max_length=5, unique=True)


class ReadingTypes(models.Model):
    reading_type = models.CharField(max_length=20, unique=True)


class ReadingConditionTypes(models.Model):
    reading_condition_type = models.CharField(max_length=50, unique=True)


class StationReadings(models.Model):
    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    measure = models.FloatField()
    # units = models.ForeignKey(Units)
    datetime = models.DateTimeField()
    # reading_type = models.ForeignKey(ReadingTypes)


class Alert(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    station = models.ForeignKey(Stations, on_delete=models.CASCADE)
    reading_type = models.ForeignKey(ReadingTypes)
    reading_condition_type_id = models.ForeignKey(ReadingConditionTypes)
    reading_min = models.FloatField(null=True)
    reading_max = models.FloatField(null=True)

    def clean(self):
        if self.reading_min is None and self.reading_max is None:
            raise ValidationError('There must be at least one reading.')