# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 20:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_exchangerate'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='num_players',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='prize_amount',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='base_currency',
            field=models.IntegerField(choices=[(10, 'ETH'), (20, 'BTC'), (30, 'USD')]),
        ),
        migrations.AlterField(
            model_name='exchangerate',
            name='currency',
            field=models.IntegerField(choices=[(10, 'ETH'), (20, 'BTC'), (30, 'USD')]),
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.IntegerField(choices=[(0, 'New'), (10, 'Published (Still can buy a ticket)'), (20, 'Canceled (no winner)'), (30, 'Finished (has winner)')], default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='type',
            field=models.IntegerField(choices=[(10, '1 day'), (30, '7 days'), (30, '30 days')]),
        ),
    ]