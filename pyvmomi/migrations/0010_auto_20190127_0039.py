# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-26 21:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pyvmomi', '0009_disc_route'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Disc',
            new_name='Disk',
        ),
    ]