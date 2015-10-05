# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jobs.models


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('state', models.IntegerField(default=1, choices=[(1, 'Recebido'), (2, 'Em processamento'), (3, 'Concluído'), (4, 'Erro')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_file', models.FileField(upload_to=jobs.models.report_filename, blank=True)),
                ('audit', models.ForeignKey(to='audits.Audit')),
                ('documents', models.ManyToManyField(to='audits.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
