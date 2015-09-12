# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lumina', '0009_auto_20150912_2003'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='sessiontype',
            unique_together=set([('studio', 'name')]),
        ),
    ]
