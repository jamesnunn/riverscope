# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-16 22:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stations', '0005_auto_20170416_2228'),
    ]

    operations = [
        migrations.AlterField(
            model_name='stations',
            name='label',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='stations',
            name='river_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='stations',
            name='stage_scale_url',
            field=models.CharField(max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='stations',
            name='town',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
