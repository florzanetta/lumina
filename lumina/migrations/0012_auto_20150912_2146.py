# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0011_auto_20150912_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionquote',
            name='session',
            field=models.ForeignKey(to='lumina.Session', verbose_name='Sesión', on_delete=django.db.models.deletion.SET_NULL, related_name='quotes', blank=True, null=True),
        ),
    ]
