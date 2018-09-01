# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('number', models.CharField(max_length=7, serialize=False, primary_key=True)),
                ('room_number', models.IntegerField()),
                ('status', models.CharField(default=b'AVAILABLE', max_length=9, choices=[(b'OFF', b'Off'), (b'INUSE', b'In Use'), (b'AVAILABLE', b'Available'), (b'ERROR', b'Error')])),
                ('used_for', models.CharField(max_length=40, blank=True)),
                ('last_update', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CourseUsageInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course', models.CharField(max_length=20)),
                ('num_machines', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Lab',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('course_name', models.CharField(max_length=30)),
                ('room_number', models.IntegerField()),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('day_of_week', models.IntegerField(max_length=1)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RoomInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lab', models.CharField(max_length=10)),
                ('num_reporting', models.IntegerField()),
                ('num_available', models.IntegerField()),
                ('num_unavailable', models.IntegerField()),
                ('num_error', models.IntegerField()),
                ('last_updated', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='courseusageinfo',
            name='room',
            field=models.ForeignKey(related_name='cuis', to='computers.RoomInfo'),
            preserve_default=True,
        ),
    ]
