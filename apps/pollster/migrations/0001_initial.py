# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20160608_1535'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shortname', models.SlugField(max_length=255)),
                ('chartwrapper', models.TextField(default=b'', blank=True)),
                ('sqlsource', models.TextField(default=b'', verbose_name=b'SQL Source Query', blank=True)),
                ('sqlfilter', models.CharField(default=b'NONE', max_length=255, verbose_name=b'Results Filter', choices=[(b'NONE', b'None'), (b'USER', b'Current User'), (b'PERSON', b'Current Person')])),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'DRAFT', max_length=255, choices=[(b'DRAFT', b'Draft'), (b'PUBLISHED', b'Published')])),
                ('geotable', models.CharField(default=b'pollster_zip_codes', max_length=255, choices=[(b'pollster_zip_codes', b'zip level')])),
            ],
            options={
                'ordering': ['survey', 'shortname'],
            },
        ),
        migrations.CreateModel(
            name='ChartType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shortname', models.SlugField(unique=True, max_length=255)),
                ('description', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_virtual', models.BooleanField(default=False)),
                ('is_open', models.BooleanField(default=False)),
                ('starts_hidden', models.BooleanField(default=False)),
                ('ordinal', models.IntegerField()),
                ('text', models.CharField(default=b'', max_length=4095, blank=True)),
                ('group', models.CharField(default=b'', max_length=255, blank=True)),
                ('value', models.CharField(default=b'', max_length=255)),
                ('description', models.TextField(default=b'', blank=True)),
                ('virtual_inf', models.CharField(default=b'', max_length=255, blank=True)),
                ('virtual_sup', models.CharField(default=b'', max_length=255, blank=True)),
                ('virtual_regex', models.CharField(default=b'', max_length=255, blank=True)),
                ('clone', models.ForeignKey(blank=True, to='pollster.Option', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['question', 'ordinal'],
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starts_hidden', models.BooleanField(default=False)),
                ('is_mandatory', models.BooleanField(default=False)),
                ('ordinal', models.IntegerField()),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('type', models.CharField(max_length=255, choices=[(b'builtin', b'Builtin'), (b'text', b'Open Answer'), (b'single-choice', b'Single Choice'), (b'multiple-choice', b'Multiple Choice'), (b'matrix-select', b'Matrix Select'), (b'matrix-entry', b'Matrix Entry')])),
                ('data_name', models.CharField(max_length=255)),
                ('visual', models.CharField(default=b'', max_length=255, blank=True)),
                ('tags', models.CharField(default=b'', max_length=255, blank=True)),
                ('regex', models.CharField(default=b'', max_length=1023, blank=True)),
                ('error_message', models.TextField(default=b'', blank=True)),
            ],
            options={
                'ordering': ['survey', 'ordinal'],
            },
        ),
        migrations.CreateModel(
            name='QuestionColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.IntegerField()),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('question', models.ForeignKey(related_name='column_set', to='pollster.Question', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['question', 'ordinal'],
            },
        ),
        migrations.CreateModel(
            name='QuestionDataType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('db_type', models.CharField(max_length=255)),
                ('css_class', models.CharField(max_length=255)),
                ('js_class', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ordinal', models.IntegerField()),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('question', models.ForeignKey(related_name='row_set', to='pollster.Question', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['question', 'ordinal'],
            },
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_sufficient', models.BooleanField(default=True)),
                ('object_options', models.ManyToManyField(related_name='object_of_rules', to='pollster.Option')),
                ('object_question', models.ForeignKey(related_name='object_of_rules', blank=True, to='pollster.Question', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='RuleType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('js_class', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Survey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('shortname', models.SlugField(default=b'', max_length=255)),
                ('version', models.SlugField(default=b'', max_length=255, blank=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(default=b'DRAFT', help_text=b'Use full editor to publish and unpublish', max_length=255, choices=[(b'DRAFT', b'Draft'), (b'PUBLISHED', b'Published'), (b'UNPUBLISHED', b'Unpublished')])),
                ('parent', models.ForeignKey(blank=True, to='pollster.Survey', null=True, on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SurveyChartPlugin',
            fields=[
                ('cmsplugin_ptr', models.OneToOneField(parent_link=True, related_name='pollster_surveychartplugin', auto_created=True, primary_key=True, serialize=False, to='cms.CMSPlugin', on_delete=django.db.models.deletion.CASCADE)),
                ('chart', models.ForeignKey(to='pollster.Chart', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'abstract': False,
            },
            bases=('cms.cmsplugin',),
        ),
        migrations.CreateModel(
            name='TranslationOption',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(default=b'', max_length=4095, blank=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('option', models.ForeignKey(to='pollster.Option', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['translation', 'option'],
            },
        ),
        migrations.CreateModel(
            name='TranslationQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('description', models.TextField(default=b'', blank=True)),
                ('error_message', models.TextField(default=b'', blank=True)),
                ('question', models.ForeignKey(to='pollster.Question', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['translation', 'question'],
            },
        ),
        migrations.CreateModel(
            name='TranslationQuestionColumn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('column', models.ForeignKey(to='pollster.QuestionColumn', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['translation', 'column'],
            },
        ),
        migrations.CreateModel(
            name='TranslationQuestionRow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('row', models.ForeignKey(to='pollster.QuestionRow', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['translation', 'row'],
            },
        ),
        migrations.CreateModel(
            name='TranslationSurvey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('language', models.CharField(max_length=3, db_index=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('status', models.CharField(default=b'DRAFT', max_length=255, choices=[(b'DRAFT', b'Draft'), (b'PUBLISHED', b'Published')])),
                ('survey', models.ForeignKey(to='pollster.Survey', on_delete=django.db.models.deletion.CASCADE)),
            ],
            options={
                'ordering': ['survey', 'language'],
                'verbose_name': 'Translation',
            },
        ),
        migrations.CreateModel(
            name='VirtualOptionType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(default=b'', max_length=255, blank=True)),
                ('js_class', models.CharField(unique=True, max_length=255)),
                ('question_data_type', models.ForeignKey(to='pollster.QuestionDataType', on_delete=django.db.models.deletion.CASCADE)),
            ],
        ),
        migrations.AddField(
            model_name='translationquestionrow',
            name='translation',
            field=models.ForeignKey(to='pollster.TranslationSurvey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='translationquestioncolumn',
            name='translation',
            field=models.ForeignKey(to='pollster.TranslationSurvey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='translationquestion',
            name='translation',
            field=models.ForeignKey(to='pollster.TranslationSurvey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='translationoption',
            name='translation',
            field=models.ForeignKey(to='pollster.TranslationSurvey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='rule',
            name='rule_type',
            field=models.ForeignKey(to='pollster.RuleType', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='rule',
            name='subject_options',
            field=models.ManyToManyField(related_name='subject_of_rules', to='pollster.Option'),
        ),
        migrations.AddField(
            model_name='rule',
            name='subject_question',
            field=models.ForeignKey(related_name='subject_of_rules', to='pollster.Question', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='question',
            name='data_type',
            field=models.ForeignKey(to='pollster.QuestionDataType', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='question',
            name='open_option_data_type',
            field=models.ForeignKey(related_name='questions_with_open_option', blank=True, to='pollster.QuestionDataType', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='question',
            name='survey',
            field=models.ForeignKey(to='pollster.Survey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='option',
            name='column',
            field=models.ForeignKey(blank=True, to='pollster.QuestionColumn', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='option',
            name='question',
            field=models.ForeignKey(to='pollster.Question', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='option',
            name='row',
            field=models.ForeignKey(blank=True, to='pollster.QuestionRow', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='option',
            name='virtual_type',
            field=models.ForeignKey(blank=True, to='pollster.VirtualOptionType', null=True, on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='chart',
            name='survey',
            field=models.ForeignKey(to='pollster.Survey', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AddField(
            model_name='chart',
            name='type',
            field=models.ForeignKey(to='pollster.ChartType', on_delete=django.db.models.deletion.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='translationsurvey',
            unique_together=set([('survey', 'language')]),
        ),
        migrations.AlterUniqueTogether(
            name='translationquestionrow',
            unique_together=set([('translation', 'row')]),
        ),
        migrations.AlterUniqueTogether(
            name='translationquestioncolumn',
            unique_together=set([('translation', 'column')]),
        ),
        migrations.AlterUniqueTogether(
            name='translationquestion',
            unique_together=set([('translation', 'question')]),
        ),
        migrations.AlterUniqueTogether(
            name='translationoption',
            unique_together=set([('translation', 'option')]),
        ),
        migrations.AlterUniqueTogether(
            name='chart',
            unique_together=set([('survey', 'shortname')]),
        ),
    ]
