# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 21:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0007_auto_20170416_2244'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReadingType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reading_type', models.CharField(max_length=20, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='StationReadings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measure', models.FloatField()),
                ('datetime', models.DateTimeField()),
                ('reading_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.ReadingType')),
                ('station_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.Stations')),
            ],
        ),
        migrations.CreateModel(
            name='Units',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unit', models.CharField(max_length=5, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='stationreadings',
            name='units',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.Units'),
        ),
    ]