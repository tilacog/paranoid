# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('execution_script', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('parsing_instructions', models.CharField(max_length=4096, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('checksum', models.CharField(max_length=40, blank=True)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('uploaded_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='KeyValueFormStore',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('key', models.CharField(max_length=30)),
                ('value', models.CharField(max_length=120, blank=True)),
                ('tag', models.CharField(max_length=30, blank=True)),
                ('form_field_class', models.CharField(max_length=30)),
                ('input_label', models.CharField(max_length=30)),
                ('tooltip_text', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='audit',
            name='extra_audit_info',
            field=models.ManyToManyField(related_name='as_audit_tags', to='audits.KeyValueFormStore'),
        ),
        migrations.AddField(
            model_name='audit',
            name='extra_doctype_info',
            field=models.ManyToManyField(related_name='as_doctype_tags', to='audits.KeyValueFormStore'),
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
