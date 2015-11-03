# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import jobs.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('audits', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('state', models.IntegerField(default=1, choices=[(1, 'Recebido'), (2, 'Em processamento'), (3, 'Concluído'), (4, 'Erro')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_file', models.FileField(blank=True, upload_to=jobs.models.report_filename)),
                ('audit', models.ForeignKey(to='audits.Audit')),
                ('documents', models.ManyToManyField(to='audits.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
