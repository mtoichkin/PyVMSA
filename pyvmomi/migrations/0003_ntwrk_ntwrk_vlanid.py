# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-14 20:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyvmomi', '0002_ntwrk'),
    ]

    operations = [
        migrations.AddField(
            model_name='ntwrk',
            name='ntwrk_vlanid',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=False,
        ),
    ]