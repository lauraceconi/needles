# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-06 22:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='localdeinteresse',
            name='foto',
            field=models.ImageField(blank=True, null=True, upload_to='images'),
        ),
    ]
