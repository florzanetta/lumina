# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='original_file_checksum',
            field=models.CharField(verbose_name='checksum de archivo original', blank=True, max_length=64, null=True),
        ),
    ]
