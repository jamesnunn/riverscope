# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-04-19 21:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stations', '0008_auto_20170419_2145'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alert',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reading_min', models.FloatField(null=True)),
                ('reading_max', models.FloatField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReadingConditionTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reading_condition_type', models.CharField(max_length=50, unique=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='ReadingType',
            new_name='ReadingTypes',
        ),
        migrations.AddField(
            model_name='alert',
            name='reading_condition_type_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.ReadingConditionTypes'),
        ),
        migrations.AddField(
            model_name='alert',
            name='reading_type_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.ReadingTypes'),
        ),
        migrations.AddField(
            model_name='alert',
            name='station_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='stations.Stations'),
        ),
        migrations.AddField(
            model_name='alert',
            name='user_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]