# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0010_auto_20150912_2014'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customertype',
            options={'verbose_name_plural': 'tipos de cliente', 'verbose_name': 'tipo de cliente'},
        ),
        migrations.AlterModelOptions(
            name='previewsize',
            options={'ordering': ['max_size'], 'verbose_name_plural': 'tamaños de previsualización', 'verbose_name': 'tamaño de previsualización'},
        ),
        migrations.AlterModelOptions(
            name='sessiontype',
            options={'verbose_name_plural': 'tipos de sesión', 'verbose_name': 'tipo de sesión'},
        ),
        migrations.AlterField(
            model_name='customertype',
            name='name',
            field=models.CharField(max_length=100, verbose_name='nombre'),
        ),
        migrations.AlterField(
            model_name='sessiontype',
            name='name',
            field=models.CharField(max_length=100, verbose_name='nombre'),
        ),
        migrations.AlterUniqueTogether(
            name='customertype',
            unique_together=set([('studio', 'name')]),
        ),
    ]
