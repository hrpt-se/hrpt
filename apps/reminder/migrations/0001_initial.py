# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FailedEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.CharField(max_length=255)),
                ('traceback', models.TextField()),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='ManualNewsLetter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('sender_email', models.EmailField(max_length=254)),
                ('sender_name', models.CharField(max_length=255)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='NewsLetter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(unique=True, verbose_name='Datum')),
                ('sender_email', models.EmailField(help_text=b'Only use email addresses for your main domain to ensure deliverability', max_length=254, verbose_name='Avs\xe4ndarens E-post')),
                ('sender_name', models.CharField(max_length=255, verbose_name='Avs\xe4ndares Namn')),
                ('published', models.BooleanField(default=True, help_text=b'Uncheck this box to postpone sending of this newsletter until the box is checked.', verbose_name=b'Is published')),
            ],
            options={
                'ordering': ('-date',),
            },
        ),
        migrations.CreateModel(
            name='NewsLetterTemplate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_default_reminder', models.BooleanField(help_text='Om detta alternativ \xe4r markerat denna mall \xe4r den standard mallen f\xf6r p\xe5minnelse e-post.', verbose_name='\xc4r standard p\xe5minnelse')),
                ('is_default_newsitem', models.BooleanField(help_text='Om detta alternativ \xe4r markerat denna mall \xe4r den standardmall f\xf6r nya nyheter.', verbose_name='\xc4r standard nyhet')),
                ('sender_email', models.EmailField(help_text=b'Only use email addresses for your main domain to ensure deliverability', max_length=254, verbose_name='Avs\xe4ndarens E-post')),
                ('sender_name', models.CharField(max_length=255, verbose_name='Avs\xe4ndares Namn')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='NewsLetterTemplateTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField(help_text=b'The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url.')),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='reminder.NewsLetterTemplate', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'reminder_newslettertemplate_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='NewsLetterTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField(help_text=b'The strings {{ url }} and {{ unsubscribe_url }} may be used to refer to the profile url and unsubscribe url.')),
                ('language_code', models.CharField(max_length=15, db_index=True)),
                ('master', models.ForeignKey(related_name='translations', editable=False, to='reminder.NewsLetter', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'managed': True,
                'abstract': False,
                'db_table': 'reminder_newsletter_translation',
                'db_tablespace': '',
                'default_permissions': (),
            },
        ),
        migrations.CreateModel(
            name='QueuedEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('manual_newsletter', models.ForeignKey(to='reminder.ManualNewsLetter', on_delete=django.db.models.deletion.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='ReminderError',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('message', models.CharField(max_length=255)),
                ('traceback', models.TextField()),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
        migrations.CreateModel(
            name='ReminderSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('send_reminders', models.BooleanField(help_text='Kryssa i den h\xe4r boxen f\xf6r att skicka p\xe5minnelser', verbose_name='Skicka p\xe5minnelser')),
                ('interval', models.IntegerField(blank=True, null=True, verbose_name='Interval', choices=[(7, 'Veckovis'), (14, 'Varannan vecka'), (-1, "Don't send reminders at a fixed interval"), (-2, b'Send exactly 7 days after the last action was taken.')])),
                ('begin_date', models.DateTimeField(help_text=b'Date & time of the first reminder and point of reference for subsequent reminders; (Time zone: Europe/Amsterdam)', null=True, verbose_name='Startdatum', blank=True)),
                ('batch_size', models.IntegerField(help_text=b"Batch size determines the max. sent emails per call to 'reminder_send'; choose in coordinance with you r crontab interval and total users; Leave empty to not have any maximum", null=True, verbose_name=b'Batch size', blank=True)),
                ('currently_sending', models.BooleanField(default=False, help_text=b"This indicates if the reminders are being sent right now. Don't tick this box unless you absolutely know what you're doing", verbose_name=b'Currently sending')),
                ('last_process_started_date', models.DateTimeField(help_text=b"This indicates if the reminders are being sent right now. Don't change this value unless you absolutely know what you're doing", verbose_name=b'Last process started at')),
                ('site', models.OneToOneField(to='sites.Site', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SentEmail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('queued', models.DateTimeField()),
                ('sent', models.DateTimeField(auto_now_add=True)),
                ('manual_newsletter', models.ForeignKey(to='reminder.ManualNewsLetter', on_delete=django.db.models.deletion.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='UserReminderInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_reminder', models.DateTimeField(null=True, blank=True)),
                ('active', models.BooleanField()),
                ('language', models.CharField(max_length=5, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, unique=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='manualnewsletter',
            name='template',
            field=models.ForeignKey(to='reminder.NewsLetterTemplate', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='failedemail',
            name='manual_newsletter',
            field=models.ForeignKey(to='reminder.ManualNewsLetter', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='failedemail',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='newslettertranslation',
            unique_together=set([('language_code', 'master')]),
        ),
        migrations.AlterUniqueTogether(
            name='newslettertemplatetranslation',
            unique_together=set([('language_code', 'master')]),
        ),
    ]
