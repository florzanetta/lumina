# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0004_session_album_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='customertype',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Archivado'),
        ),
    ]
