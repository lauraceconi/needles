# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-19 22:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20181013_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classificacao',
            name='descricao',
            field=models.CharField(choices=[(1, 'Amigo'), (2, 'Conhecido'), (3, 'N\xe3o conhe\xe7o'), (4, 'Inimigo')], max_length=30, verbose_name='Descri\xe7\xe3o'),
        ),
    ]