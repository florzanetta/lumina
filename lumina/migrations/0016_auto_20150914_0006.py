# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0015_auto_20150914_0004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessionquote',
            name='stipulated_date',
            field=models.DateField(verbose_name='fecha de entrega pactada'),
        ),
    ]
