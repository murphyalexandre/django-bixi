# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.SlugField(max_length=20)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('active', models.BooleanField(default=True)),
                ('last_update', models.DateTimeField(null=True)),
            ],
            options={
                'get_latest_by': 'last_update',
                'verbose_name_plural': 'cities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('public_id', models.IntegerField()),
                ('name', models.CharField(max_length=200)),
                ('terminal_name', models.CharField(max_length=10)),
                ('last_comm_with_server', models.DateTimeField(null=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('installed', models.BooleanField(default=False)),
                ('locked', models.BooleanField(default=False)),
                ('install_date', models.DateTimeField(null=True)),
                ('removal_date', models.DateTimeField(null=True)),
                ('temporary', models.BooleanField(default=False)),
                ('public', models.NullBooleanField()),
                ('city', models.ForeignKey(to='bixi.City')),
            ],
            options={
                'get_latest_by': 'last_comm_with_server',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nb_bikes', models.IntegerField()),
                ('nb_empty_docks', models.IntegerField()),
                ('latest_update_time', models.DateTimeField(null=True)),
                ('station', models.ForeignKey(to='bixi.Station')),
            ],
            options={
                'get_latest_by': 'latest_update_time',
            },
            bases=(models.Model,),
        ),
    ]
