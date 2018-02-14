# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-02-14 21:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_auto_20180214_1919'),
    ]

    operations = [
        migrations.AddField(
            model_name='gameplayer',
            name='is_winner',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='gameplayer',
            name='prize_amount',
            field=models.FloatField(default=0),
        ),
    ]
