# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 16:26
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0002_stations_point'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stations',
            name='lat',
        ),
        migrations.RemoveField(
            model_name='stations',
            name='lon',
        ),
    ]
