# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tas', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='request',
            old_name='whenAsked',
            new_name='when_asked',
        ),
        migrations.RenameField(
            model_name='request',
            old_name='whenSolved',
            new_name='when_solved',
        ),
    ]
