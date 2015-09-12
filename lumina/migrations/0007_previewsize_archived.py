# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0006_sessiontype_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='previewsize',
            name='archived',
            field=models.BooleanField(default=False, verbose_name='Archivado'),
        ),
    ]
