# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-06 02:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abastecimento', '0004_auto_20161005_2315'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veiculo',
            name='observacao',
            field=models.TextField(blank=True, null=True),
        ),
    ]
