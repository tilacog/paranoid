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
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
                ('execution_script', models.CharField(max_length=4096)),
            ],
        ),
        migrations.CreateModel(
            name='Doctype',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('parsing_instructions', models.CharField(max_length=4096, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('file', models.FileField(upload_to='')),
                ('checksum', models.CharField(max_length=40, blank=True)),
                ('doctype', models.ForeignKey(to='audits.Doctype')),
                ('uploaded_by', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FormFieldRecipe',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('key', models.CharField(max_length=30)),
                ('tag', models.CharField(max_length=30, blank=True)),
                ('form_field_class', models.CharField(max_length=30, choices=[('BaseTemporalField', 'BaseTemporalField'), ('BooleanField', 'BooleanField'), ('CharField', 'CharField'), ('ChoiceField', 'ChoiceField'), ('ComboField', 'ComboField'), ('DateField', 'DateField'), ('DateTimeField', 'DateTimeField'), ('DecimalField', 'DecimalField'), ('DurationField', 'DurationField'), ('EmailField', 'EmailField'), ('FileField', 'FileField'), ('FilePathField', 'FilePathField'), ('FloatField', 'FloatField'), ('GenericIPAddressField', 'GenericIPAddressField'), ('IPAddressField', 'IPAddressField'), ('ImageField', 'ImageField'), ('IntegerField', 'IntegerField'), ('MultiValueField', 'MultiValueField'), ('MultipleChoiceField', 'MultipleChoiceField'), ('NullBooleanField', 'NullBooleanField'), ('RegexField', 'RegexField'), ('SlugField', 'SlugField'), ('SplitDateTimeField', 'SplitDateTimeField'), ('TimeField', 'TimeField'), ('TypedChoiceField', 'TypedChoiceField'), ('TypedMultipleChoiceField', 'TypedMultipleChoiceField'), ('URLField', 'URLField'), ('UUIDField', 'UUIDField')])),
                ('input_label', models.CharField(max_length=30)),
                ('tooltip_text', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Package',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=30, unique=True)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='audit',
            name='extra_audit_info',
            field=models.ManyToManyField(to='audits.FormFieldRecipe', related_name='as_audit_tags'),
        ),
        migrations.AddField(
            model_name='audit',
            name='extra_doctype_info',
            field=models.ManyToManyField(to='audits.FormFieldRecipe', related_name='as_doctype_tags'),
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
