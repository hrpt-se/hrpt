# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-10-10 15:34
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0002_newlettertemplate_newsletter_plain_managers'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userreminderinfo',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
