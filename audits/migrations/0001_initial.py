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
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('runner', models.CharField(max_length=120, choices=[('MinimalAuditRunner', 'MinimalAuditRunner')])),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('validator', models.CharField(max_length=120, choices=[('PlainTextValidator', 'PlainTextValidator')])),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('file', models.FileField(upload_to=audits.models.document_filename)),
                ('checksum', models.CharField(blank=True, max_length=40)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True)),
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
