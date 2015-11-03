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
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField()),
                ('runner', models.CharField(choices=[('MinimalAuditRunner', 'MinimalAuditRunner'), ('EfdContribuicoesRunner', 'EfdContribuicoesRunner'), ('DummyAudit', 'DummyAudit')], max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('name', models.CharField(max_length=30, serialize=False, primary_key=True)),
                ('validator', models.CharField(choices=[('DummyValidator', 'DummyValidator'), ('PlainTextValidator', 'PlainTextValidator')], max_length=120)),
                ('mime', models.CharField(default='text/plain', max_length=60)),
                ('encoding', models.CharField(default='utf_8', blank=True, choices=[('', '-----'), ('utf_8', 'utf-8'), ('iso8859-1', 'latin-1'), ('cp1252', 'windows_1252'), ('cp850', 'cp850')], max_length=25)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('file', models.FileField(upload_to=audits.models.document_filename)),
                ('checksum', models.CharField(blank=True, max_length=40)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
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
