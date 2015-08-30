# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0002_image_original_file_checksum'),
    ]

    operations = [
        migrations.AddField(
            model_name='studio',
            name='watermark_text',
            field=models.CharField(default='', max_length=40),
        ),
    ]
