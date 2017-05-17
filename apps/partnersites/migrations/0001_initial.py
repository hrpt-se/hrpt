# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('logo', models.ImageField(help_text='Preferred height: 70px, maximum width: 756px', upload_to=b'uploads', null=True, verbose_name='Logotyp', blank=True)),
                ('light_color', models.CharField(default=b'ce2626', max_length=6)),
                ('footer', models.TextField(help_text='Fotsidan visas l\xe4ngst ner p\xe5 varje sida', null=True, verbose_name='Fotsida', blank=True)),
                ('contact_form_recipient', models.EmailField(default=b'admin.halsorapport@folkhalsomyndigheten.se', max_length=254, blank=True)),
                ('site', models.OneToOneField(to='sites.Site')),
            ],
            options={
                'verbose_name': 'Sajtens Inst\xe4llningar',
                'verbose_name_plural': 'Sajtens Inst\xe4llningar',
            },
        ),
    ]
