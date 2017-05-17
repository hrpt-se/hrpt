# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='A slug is a short name which uniquely identifies the category', unique=True, verbose_name='Slug')),
            ],
            options={
                'ordering': ('slug',),
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='CategoryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='journal.Category')),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'journal_category_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(help_text='A slug is a short name which uniquely identifies the news item for this day', verbose_name='Slug', unique_for_date=b'pub_date')),
                ('image', models.ImageField(upload_to=b'journal_images', null=True, verbose_name='Image', blank=True)),
                ('alignment', models.CharField(choices=[('Left', b'left'), ('Right', b'right')], max_length=5, blank=True, help_text='Alignment of the image', null=True, verbose_name='Alignment')),
                ('is_published', models.BooleanField(default=True, verbose_name='Published')),
                ('pub_date', models.DateTimeField(default=datetime.datetime(2017, 5, 4, 12, 48, 13, 312499), verbose_name='Publication date')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(to='journal.Category', null=True)),
            ],
            options={
                'ordering': ('-pub_date',),
                'verbose_name': 'Entry',
                'verbose_name_plural': 'Entries',
            },
        ),
        migrations.CreateModel(
            name='EntryTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('excerpt', models.TextField(verbose_name='Excerpt', blank=True)),
                ('content', models.TextField(verbose_name='Content', blank=True)),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='journal.Entry')),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'journal_entry_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='LatestEntryPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='journal_latestentryplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
                ('title', models.CharField(max_length=255, verbose_name='Title')),
                ('limit', models.PositiveIntegerField(help_text='Limits the number of entries that will be displayed', verbose_name='Number of entries to show')),
                ('category', models.ManyToManyField(help_text='Leave this field blank to match all categories', to='journal.Category', null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.AlterUniqueTogether(
            name='entrytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='categorytranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
