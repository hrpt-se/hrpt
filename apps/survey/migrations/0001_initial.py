# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import apps.survey.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LastResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.TextField(default=None, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='LocalFluSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('status', models.CharField(max_length=8)),
                ('age_user', models.SmallIntegerField()),
                ('data', models.TextField()),
                ('survey_id', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LocalProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sq_num_season', models.SmallIntegerField(null=True)),
                ('sq_num_total', models.SmallIntegerField(null=True)),
                ('sq_date_first', models.DateField(null=True)),
                ('sq_date_last', models.DateField(null=True)),
                ('birth_date', models.DateField()),
                ('zip_code', models.CharField(max_length=5)),
                ('region', models.CharField(max_length=30, null=True)),
                ('gender', models.CharField(max_length=1)),
                ('a_family', models.SmallIntegerField()),
                ('a_smoker', models.CharField(max_length=1)),
                ('a_vaccine_prev_seasonal', models.CharField(max_length=1)),
                ('a_vaccine_prev_swine', models.CharField(max_length=1)),
                ('a_vaccine_current', models.CharField(max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='LocalResponse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('user_id', models.CharField(max_length=36)),
                ('survey_id', models.CharField(max_length=50)),
                ('answers', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Participation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('epidb_id', models.CharField(max_length=36, null=True)),
                ('previous_participation_date', models.DateTimeField(null=True)),
                ('previous_participation', models.ForeignKey(to='survey.Participation', null=True)),
            ],
            options={
                'verbose_name_plural': 'Survey participation log',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(default=None, null=True)),
                ('updated', models.DateTimeField(default=None, null=True)),
                ('valid', models.BooleanField(default=False)),
                ('data', models.TextField(default=None, null=True, blank=True)),
            ],
            options={
                'verbose_name_plural': 'User profile',
            },
        ),
        migrations.CreateModel(
            name='ProfileSendQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField()),
                ('user_id', models.CharField(max_length=36)),
                ('survey_id', models.CharField(max_length=50)),
                ('answers', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='ResponseSendQueue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('user_id', models.CharField(max_length=36)),
                ('survey_id', models.CharField(max_length=50)),
                ('answers', models.TextField()),
                ('participation', models.ForeignKey(to='survey.Participation')),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('survey_id', models.CharField(unique=True, max_length=50)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField(null=True, blank=True)),
                ('specification', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SurveyIdCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('surveyuser_global_id', models.CharField(max_length=36, unique=True, null=True, blank=True)),
                ('idcode', models.CharField(unique=True, max_length=10)),
                ('fodelsedatum', models.CharField(max_length=10, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyListPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='survey_surveylistplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin')),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='SurveyResposeDraft',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('global_id', models.CharField(max_length=36)),
                ('survey_id', models.IntegerField()),
                ('timestamp', models.IntegerField()),
                ('form_data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='SurveyUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('global_id', models.CharField(default=apps.survey.models.create_global_id, unique=True, max_length=36)),
                ('last_participation_date', models.DateTimeField(null=True, blank=True)),
                ('name', models.CharField(max_length=100)),
                ('deleted', models.BooleanField(default=False)),
                ('last_participation', models.ForeignKey(blank=True, to='survey.Participation', null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name_plural': 'User',
            },
        ),
        migrations.AddField(
            model_name='profilesendqueue',
            name='owner',
            field=models.ForeignKey(to='survey.SurveyUser'),
        ),
        migrations.AddField(
            model_name='profile',
            name='survey',
            field=models.ForeignKey(default=None, to='survey.Survey', null=True),
        ),
        migrations.AddField(
            model_name='profile',
            name='user',
            field=models.ForeignKey(to='survey.SurveyUser', unique=True),
        ),
        migrations.AddField(
            model_name='participation',
            name='survey',
            field=models.ForeignKey(to='survey.Survey'),
        ),
        migrations.AddField(
            model_name='participation',
            name='user',
            field=models.ForeignKey(to='survey.SurveyUser'),
        ),
        migrations.AddField(
            model_name='localprofile',
            name='surveyuser',
            field=models.ForeignKey(to='survey.SurveyUser', unique=True),
        ),
        migrations.AddField(
            model_name='localflusurvey',
            name='surveyuser',
            field=models.ForeignKey(to='survey.SurveyUser'),
        ),
        migrations.AddField(
            model_name='lastresponse',
            name='participation',
            field=models.ForeignKey(default=None, to='survey.Participation', null=True),
        ),
        migrations.AddField(
            model_name='lastresponse',
            name='user',
            field=models.ForeignKey(to='survey.SurveyUser', unique=True),
        ),
    ]
