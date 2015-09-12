# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0003_studio_watermark_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='album_icon',
            field=models.ForeignKey(to='lumina.Image', blank=True, null=True, related_name='+'),
        ),
    ]
