# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-22 11:46
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finances', '0003_auto_20160220_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lydia',
            name='time_operation',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 22, 12, 46, 40, 165806)),
        ),
    ]