# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-12-05 19:13
from __future__ import unicode_literals

from django.db import migrations
import django_countries.fields
import localflavor.us.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170509_1559'),
        ('pfb_analysis', '0032_neighborhood_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='neighborhood',
            name='country',
            field=django_countries.fields.CountryField(default='US', help_text='The country of the uploaded neighborhood', max_length=2),
        ),
        migrations.AlterField(
            model_name='neighborhood',
            name='state_abbrev',
            field=localflavor.us.models.USStateField(blank=True, help_text='The state of the uploaded neighborhood, if in the US', max_length=2, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='neighborhood',
            unique_together=set([('name', 'country', 'state_abbrev', 'organization')]),
        ),
    ]
