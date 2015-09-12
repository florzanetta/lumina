# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0005_customertype_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='sessiontype',
            name='archived',
            field=models.BooleanField(verbose_name='Archivado', default=False),
        ),
    ]
