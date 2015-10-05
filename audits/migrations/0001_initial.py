# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import audits.models
from django.conf import settings
import runner.plugins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('execution_script', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30, unique=True)),
                ('validator', models.CharField(max_length=120, choices=[('PlainTextValidator', runner.plugins.PlainTextValidator)])),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('file', models.FileField(upload_to=audits.models.document_filename)),
                ('checksum', models.CharField(max_length=40, blank=True)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
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
