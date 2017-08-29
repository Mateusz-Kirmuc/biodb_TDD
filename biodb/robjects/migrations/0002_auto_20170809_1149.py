# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-09 11:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('robjects', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tag',
            name='project',
        ),
        migrations.AlterField(
            model_name='robject',
            name='tags',
            field=models.ManyToManyField(to='projects.Tag'),
        ),
        migrations.DeleteModel(
            name='Tag',
        ),
    ]