# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jobs.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('audits', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.IntegerField(choices=[(1, 'Recebido'), (2, 'Em processamento'), (3, 'Concluído'), (4, 'Erro')], default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_file', models.FileField(blank=True, upload_to=jobs.models.report_filename)),
                ('audit', models.ForeignKey(to='audits.Audit')),
                ('documents', models.ManyToManyField(to='audits.Document')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
