# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-06 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('partnersites', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesettings',
            name='contact_form_recipient',
            field=models.EmailField(blank=True, default='admin.halsorapport@folkhalsomyndigheten.se', max_length=254),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='light_color',
            field=models.CharField(default='ce2626', max_length=6),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='logo',
            field=models.ImageField(blank=True, help_text='Preferred height: 70px, maximum width: 756px', null=True, upload_to='uploads', verbose_name='Logotyp'),
        ),
    ]
