# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-26 22:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyvmomi', '0011_auto_20190127_0054'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disk',
            name='discpath',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]