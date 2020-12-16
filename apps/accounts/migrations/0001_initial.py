# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='user_profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('yearofbirth', models.IntegerField()),
                ('idcode', models.CharField(max_length=10)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
    ]
