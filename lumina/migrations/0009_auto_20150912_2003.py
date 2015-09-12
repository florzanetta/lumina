# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0008_auto_20150912_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='session',
            name='customer',
            field=models.ForeignKey(to='lumina.Customer', default=None, verbose_name='cliente'),
            preserve_default=False,
        ),
    ]
