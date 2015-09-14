# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0014_auto_20150913_2158'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sessionquote',
            name='give_full_quality_images',
        ),
        migrations.AlterField(
            model_name='studio',
            name='default_terms',
            field=models.TextField(verbose_name='Términos y condiciones por default'),
        ),
    ]
