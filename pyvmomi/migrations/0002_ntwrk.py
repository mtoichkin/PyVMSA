# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2019-01-14 20:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pyvmomi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ntwrk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ntwrk_name', models.CharField(max_length=50)),
            ],
        ),
    ]