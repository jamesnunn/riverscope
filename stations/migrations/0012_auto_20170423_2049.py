# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-23 20:49
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0011_auto_20170423_2037'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stationreadings',
            name='reading_type',
        ),
        migrations.RemoveField(
            model_name='stationreadings',
            name='units',
        ),
    ]