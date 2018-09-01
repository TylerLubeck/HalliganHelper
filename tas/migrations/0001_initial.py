# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import tas.models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('email', models.EmailField(help_text=b'User Identifier', unique=True, max_length=254, verbose_name=b'Email Address')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_staff', models.BooleanField(default=False, help_text=b'Whether or not the user can login to the admin site', verbose_name=b'Staff Status')),
                ('is_active', models.BooleanField(default=True, help_text=b'If the user is active or not', verbose_name=b'Active')),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The name of the course', max_length=100)),
                ('department', models.CharField(help_text=b'The department the course belongs to', max_length=50)),
                ('number', models.IntegerField(help_text=b'The identifying course number')),
            ],
            options={
                'ordering': ['department', 'number'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OfficeHour',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField(help_text=b'When the TA went on duty')),
                ('end_time', models.DateTimeField(help_text=b'When the TA goes off duty')),
                ('location', models.CharField(help_text=b'The home base of the TA', max_length=255)),
                ('course', models.ForeignKey(help_text=b'The course this OfficeHour is associated with', to='tas.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.CharField(help_text=b'The question associated with the request', max_length=51, validators=[tas.models.not_empty_string])),
                ('where_located', models.CharField(help_text=b'Where the user is located', max_length=50, validators=[tas.models.not_empty_string])),
                ('whenAsked', models.DateTimeField(help_text=b'When the request was made')),
                ('cancelled', models.BooleanField(default=False, help_text=b'Did the student cancel the request?')),
                ('solved', models.BooleanField(default=False, help_text=b'Has the request been resolved?')),
                ('whenSolved', models.DateTimeField(help_text=b'When the request was resolved', null=True, blank=True)),
                ('checked_out', models.BooleanField(default=False, help_text=b'Has a TA started working on the request?')),
                ('course', models.ForeignKey(help_text=b'The course the request is for', to='tas.Course')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TA',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('active', models.BooleanField(default=True, help_text=b'Whether or not the TA is currently active')),
                ('headshot', models.ImageField(default=b'headshots/None/ming.jpg', help_text=b'A headshot to help students identify TAs', upload_to=b'headshots')),
                ('has_updated_headshot', models.BooleanField(default=False, help_text=b'Whether or not the TA has updated their headshot')),
                ('course', models.ManyToManyField(help_text=b'The courses a TA is registered to TA for', to='tas.Course')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL, help_text=b'The user the TA is associated with.')),
            ],
            options={
                'verbose_name': "Teacher's Assistant",
                'verbose_name_plural': "Teacher's Assistants",
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='request',
            name='student',
            field=models.ForeignKey(help_text=b'The student who made the request', to='tas.Student'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='request',
            name='who_solved',
            field=models.ForeignKey(blank=True, to='tas.TA', help_text=b'The TA who resolved the request', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='officehour',
            name='ta',
            field=models.ForeignKey(help_text=b'The TA on duty', to='tas.TA'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ForeignKey(blank=True, to='tas.Student', help_text=b'A list of students enrolled in the course', null=True),
            preserve_default=True,
        ),
    ]
