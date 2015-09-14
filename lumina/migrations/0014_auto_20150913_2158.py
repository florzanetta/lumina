# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0013_auto_20150913_0053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studio',
            name='default_terms',
            field=models.TextField(default='', verbose_name='Términos y condiciones'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='studio',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Nombre del estudio'),
        ),
        migrations.AlterField(
            model_name='studio',
            name='watermark_text',
            field=models.CharField(verbose_name='Marca de agua', default='', max_length=40),
        ),
    ]
