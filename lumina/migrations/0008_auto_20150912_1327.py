# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0007_previewsize_archived'),
    ]

    operations = [
        migrations.AlterField(
            model_name='previewsize',
            name='max_size',
            field=models.PositiveIntegerField(default=0, verbose_name='Tamaño máximo'),
            preserve_default=False,
        ),
    ]
