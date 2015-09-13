# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0012_auto_20150912_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='session_type',
            field=models.ForeignKey(verbose_name='tipo de sesión', default=None, related_name='+', to='lumina.SessionType'),
            preserve_default=False,
        ),
    ]
