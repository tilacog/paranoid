# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-13 12:20
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('squeeze', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='squeezejob',
            name='job',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='jobs.Job'),
        ),
    ]
