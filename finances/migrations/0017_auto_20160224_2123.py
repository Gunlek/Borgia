# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-24 20:23
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0016_auto_20160224_2121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lydia',
            name='time_operation',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 24, 21, 23, 31, 100443)),
        ),
    ]
