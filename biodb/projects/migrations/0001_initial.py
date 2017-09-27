# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-27 11:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
            options={
                'permissions': (('can_visit_project', 'User can see project elements.'), ('can_modify_project', 'User can modify project elements.')),
            },
        ),
    ]
