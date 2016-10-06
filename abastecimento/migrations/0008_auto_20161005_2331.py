# -*- coding: utf-8 -*-
# Generated by Django 1.9.8 on 2016-10-06 02:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('abastecimento', '0007_auto_20161005_2322'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='atualizado_date',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Data Atualizado'),
        ),
        migrations.AlterField(
            model_name='abastecimento',
            name='criado_date',
            field=models.DateField(verbose_name='Data Abastecimento'),
        ),
        migrations.AlterField(
            model_name='abastecimento',
            name='quantidade',
            field=models.FloatField(verbose_name='Quantidade em Litros'),
        ),
        migrations.AlterField(
            model_name='abastecimento',
            name='valor',
            field=models.FloatField(verbose_name='Valor Pago'),
        ),
        migrations.AlterField(
            model_name='posto',
            name='criado_date',
            field=models.DateField(auto_now_add=True, verbose_name='Data Criada'),
        ),
        migrations.AlterField(
            model_name='veiculo',
            name='criado_date',
            field=models.DateField(auto_now_add=True, verbose_name='Data Criada'),
        ),
    ]
