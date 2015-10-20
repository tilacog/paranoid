# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import audits.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField()),
                ('runner', models.CharField(choices=[('MinimalAuditRunner', 'MinimalAuditRunner')], max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('name', models.CharField(serialize=False, primary_key=True, max_length=30)),
                ('validator', models.CharField(choices=[('PlainTextValidator', 'PlainTextValidator')], max_length=120)),
                ('mime', models.CharField(max_length=60, default='text/plain')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=audits.models.document_filename)),
                ('checksum', models.CharField(blank=True, max_length=40)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='audit',
            name='package',
            field=models.ForeignKey(to='audits.Package'),
        ),
        migrations.AddField(
            model_name='audit',
            name='required_doctypes',
            field=models.ManyToManyField(to='audits.Doctype'),
        ),
    ]
