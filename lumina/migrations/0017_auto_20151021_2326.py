# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0016_auto_20150914_0006'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageselection',
            name='preview_size',
            field=models.ForeignKey(null=True, to='lumina.PreviewSize', verbose_name='tamaño de previsualización'),
        ),
    ]
