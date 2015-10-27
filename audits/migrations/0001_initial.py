# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import audits.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('runner', models.CharField(max_length=120, choices=[('DummyAudit', 'DummyAudit'), ('EfdContribuicoesRunner', 'EfdContribuicoesRunner'), ('MinimalAuditRunner', 'MinimalAuditRunner')])),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('validator', models.CharField(max_length=120, choices=[('DummyValidator', 'DummyValidator'), ('PlainTextValidator', 'PlainTextValidator')])),
                ('mime', models.CharField(max_length=60, default='text/plain')),
                ('expected_encoding', models.CharField(max_length=25, choices=[('', '-----'), ('utf_8', 'utf-8'), ('iso8859-1', 'latin-1'), ('cp1252', 'windows_1252'), ('cp850', 'cp850')], blank=True, default='utf_8')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('file', models.FileField(upload_to=audits.models.document_filename)),
                ('checksum', models.CharField(max_length=40, blank=True)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
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
