# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('uuid', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('from_email', models.CharField(blank=True, max_length=1024)),
                ('to_email', models.TextField(blank=True)),
                ('body_text', models.TextField(blank=True)),
                ('body_html', models.TextField(blank=True)),
                ('subject', models.CharField(blank=True, max_length=1024)),
                ('data', models.TextField(blank=True, editable=False)),
                ('retry_count', models.SmallIntegerField(default=-1)),
                ('status', models.SmallIntegerField(choices=[(10, 'Draft'), (30, 'Sent'), (40, 'Failed'), (50, 'Discarded')], default=10)),
                ('priority', models.SmallIntegerField(default=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(default=None, null=True)),
                ('exception', models.TextField(blank=True)),
            ],
            options={
                'verbose_name': 'Message',
                'ordering': ['created_at'],
                'verbose_name_plural': 'Messages',
            },
        ),
    ]
