# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-06 10:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reminder', '0004_auto_20201001_1132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newsletter',
            name='published',
            field=models.BooleanField(default=True, help_text='Uncheck this box to postpone sending of this newsletter until the box is checked.', verbose_name='Is published'),
        ),
        migrations.AlterField(
            model_name='newsletter',
            name='sender_email',
            field=models.EmailField(help_text='Only use email addresses for your main domain to ensure deliverability', max_length=254, verbose_name='Avsändarens E-post'),
        ),
        migrations.AlterField(
            model_name='newslettertemplate',
            name='sender_email',
            field=models.EmailField(help_text='Only use email addresses for your main domain to ensure deliverability', max_length=254, verbose_name='Avsändarens E-post'),
        ),
        migrations.AlterField(
            model_name='newslettertemplatetranslation',
            name='message',
            field=models.TextField(help_text='The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url.'),
        ),
        migrations.AlterField(
            model_name='newslettertranslation',
            name='message',
            field=models.TextField(help_text='The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url.'),
        ),
        migrations.AlterField(
            model_name='remindersettings',
            name='batch_size',
            field=models.IntegerField(blank=True, help_text="Batch size determines the max. sent emails per call to 'reminder_send'; choose in coordinance with your crontab interval and total users; Leave empty to not have any maximum", null=True, verbose_name='Batch size'),
        ),
        migrations.AlterField(
            model_name='remindersettings',
            name='begin_date',
            field=models.DateTimeField(blank=True, help_text='Date & time of the first reminder and point of reference for subsequent reminders; (Time zone: Europe/Amsterdam)', null=True, verbose_name='Startdatum'),
        ),
        migrations.AlterField(
            model_name='remindersettings',
            name='currently_sending',
            field=models.BooleanField(default=False, help_text="This indicates if the reminders are being sent right now. Don't tick this box unless you absolutely know what you're doing", verbose_name='Currently sending'),
        ),
        migrations.AlterField(
            model_name='remindersettings',
            name='interval',
            field=models.IntegerField(blank=True, choices=[(7, 'Veckovis'), (14, 'Varannan vecka'), (-1, "Don't send reminders at a fixed interval"), (-2, 'Send exactly 7 days after the last action was taken.')], null=True, verbose_name='Interval'),
        ),
        migrations.AlterField(
            model_name='remindersettings',
            name='last_process_started_date',
            field=models.DateTimeField(help_text="This indicates if the reminders are being sent right now. Don't change this value unless you absolutely know what you're doing", verbose_name='Last process started at'),
        ),
    ]
