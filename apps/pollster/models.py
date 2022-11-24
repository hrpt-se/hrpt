# -*- coding: utf-8 -*-
import datetime
from math import pi, sin, log, exp, atan
import os
import shutil
import re
import json

from django.dispatch import receiver
from django.db.models.signals import pre_delete
from django.urls import reverse
from django.contrib.gis.db.models import MultiPolygonField
from django.db import (
    models, connection, transaction, IntegrityError, DatabaseError
)
from django.db.models import Count
from django.contrib.auth.models import User, Group
from django.forms import ModelForm
from django.core.validators import RegexValidator
from django.conf import settings

from cms.models import CMSPlugin
from . import dynamicmodels
from apps.survey.models import SurveyIdCode, SurveyUser

import emoji


DEG_TO_RAD = pi/180
RAD_TO_DEG = 180/pi


#TODO: remove this. Seriously, this should either work or not work.
#TODO: actuallym the whole map thing should go away. There is no reason to be in
# this file.
try:
    import mapnik2 as mapnik
    mapnik_version = 2
except:
    try:
        import mapnik
        mapnik_version = 1
    except ImportError:
        mapnik_version = None
        # warnings.warn("No working version for library 'mapnik' found. Continuing without mapnik")


SURVEY_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
    ('UNPUBLISHED', 'Unpublished')
)

SURVEY_TRANSLATION_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published')
)

CHART_STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('PUBLISHED', 'Published'),
)

QUESTION_TYPE_CHOICES = (
    ('builtin', 'Builtin'),
    ('text', 'Open Answer'),
    ('single-choice', 'Single Choice'),
    ('multiple-choice', 'Multiple Choice'),
    ('matrix-select', 'Matrix Select'),
    ('matrix-entry', 'Matrix Entry'),
    ('matrix-check', 'Matrix Check'),
)

CHART_SQLFILTER_CHOICES = (
    ('NONE', 'None'),
    ('USER', 'Current User'),
    ('PERSON', 'Current Person'),
)

IDENTIFIER_REGEX = r'^[a-zA-Z][a-zA-Z0-9_]*$'
IDENTIFIER_OPTION_REGEX = r'^[a-zA-Z0-9_]*$'
EMOJI_DELIMITERS = ("@@", "@@")


# really???
def _get_or_default(queryset, default=None):
    r = queryset[0:1]
    if r:
        return r[0]
    return default


class SurveyGroup(models.Model):
    all_active = models.BooleanField(default=True)
    groups = models.ManyToManyField(Group, related_name="survey_groups")
    users = models.ManyToManyField(User, related_name="survey_groups")

    # Filter fields used to filter users by year of birth
    from_year = models.PositiveSmallIntegerField(null=True)
    to_year = models.PositiveSmallIntegerField(null=True)

    from_joined = models.DateField(null=True)
    to_joined = models.DateField(null=True)

    def has_filter(self):
        return self.from_year or self.to_year or self.from_joined or self.to_joined

    def get_filter(self):
        query = {}
        gte = "__gte"
        lte = "__lte"

        year_query = "surveyuser__surveyidcode__fodelsedatum"
        if self.from_year:
            query[year_query + gte] = str(self.from_year)
        if self.to_year:
            query[year_query + lte] = str(self.to_year)

        joined_query = "date_joined__date"
        if self.from_joined:
            query[joined_query + gte] = self.from_joined
        if self.to_joined:
            query[joined_query + lte] = self.to_joined
        return query

    @property
    def members(self):
        if self.all_active:
            return User.objects.filter(is_active=True)
        if self.has_filter():
            if self.users.exists():
                return self.users.filter(**self.get_filter(), is_active=True)
            return User.objects.filter(**self.get_filter(), is_active=True)

        # Return the distinct union of self.users and self.groups.(users for each group)
        group_members = User.objects.filter(groups__in=self.groups.all(), is_active=True)
        return self.users.filter(is_active=True) | group_members

    def has_access(self, user: User) -> bool:
        if not user.is_active:
            return False
        if self.all_active:
            return True
        if self.has_filter():
            return User.objects.filter(pk=user.pk, **self.get_filter()).exists()
        if user.survey_groups.filter(pk=self.pk).exists():
            return True
        return user.groups.filter(pk__in=self.groups.all()).exists()


class Survey(models.Model):
    parent = models.ForeignKey('self', db_index=True, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, default='')
    shortname = models.SlugField(max_length=28, default='')
    version = models.SlugField(max_length=2, blank=True, default='')
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_STATUS_CHOICES, help_text="Use full editor to publish and unpublish")
    group = models.OneToOneField(SurveyGroup, on_delete=models.SET_NULL, related_name="survey", null=True)

    form = None
    translation_survey = None

    def save(self, *args, **kwargs):
        if not self.group:
            self.group = SurveyGroup.objects.create()
        super().save(*args, **kwargs)

    def has_access(self, user):
        if not settings.SURVEY_GROUPS or not self.group:
            return True
        return self.group.has_access(user)

    @property
    def members(self):
        if not settings.SURVEY_GROUPS or not self.group:
            return User.objects.all()
        return self.group.members

    @property
    def _standard_result_fields(self):
        return [
            ('user', models.IntegerField(unique=True, null=True, blank=True, verbose_name="User")),
            ('global_id', models.CharField(unique=True, max_length=36, null=True, blank=True, verbose_name="Person")),
            ('channel', models.CharField(max_length=36, null=True, blank=True, verbose_name="Channel")),
        ]

    @property
    def _id_existing_field(self):
        return [('id', models.BigIntegerField(primary_key=True))]

    update = False

    @property
    def shortname_max_length(self):
        return self._meta.get_field("shortname").max_length

    @property
    def q_data_name_max_length(self):
        return Question._meta.get_field("data_name").max_length

    @property
    def opt_value_max_length(self):
        return Option._meta.get_field("value").max_length

    @staticmethod
    def get_user_open_surveys(guid, user):
        published_surveys = Survey.objects.all().filter(status="PUBLISHED")
        open_surveys = []
        replied_surveys = []
        locked_surveys = []
        locked_terms_surveys = []

        # If there is an intake survey and the user has not replied to it
        # then all other open surveys should not be acessible to the user
        all_locked_by_intake = False
        all_locked_by_terms = False

        intake_survey_temp = None # just a variable to hold the intake survey while the look moves on
        terms_survey_temp = None # just a variable to hold the terms of reference survey while the look moves on

        for survey in published_surveys:
            results_table_name = "pollster_results_" + survey.shortname
            sql = "SELECT count(*) FROM " + results_table_name + " WHERE global_id = '" +guid+ "';"
            cursor = connection.cursor()
            cursor.execute(sql)
            num_rows = cursor.fetchone()[0]

            if num_rows == 0 and survey.shortname == 'intake':
                all_locked_by_intake = True
                intake_survey_temp = survey

            if num_rows == 0 and survey.shortname == 'terms':
                all_locked_by_terms = True
                terms_survey_temp = survey

            if survey.has_access(user):
                if num_rows > 0:
                    replied_surveys.append(survey)
                else:
                    open_surveys.append(survey)

        if all_locked_by_terms:
            locked_terms_surveys = [ s for s in open_surveys if not s.shortname == 'terms']
            open_surveys = [terms_survey_temp]
        else:
            if all_locked_by_intake:
                locked_surveys = [ s for s in open_surveys if not s.shortname == 'intake']
                open_surveys = [intake_survey_temp]

        return (replied_surveys, open_surveys, locked_surveys, locked_terms_surveys)


    #TODO: remove this method. just call whatever you want with django api

    @staticmethod
    def get_by_shortname(shortname):
        return Survey.objects.all().get(shortname=shortname, status="PUBLISHED")

    #TODO: delete this crazynes, this is insane
    @staticmethod
    def getHealthStatus(id):
        cursor = connection.cursor()
        sql = "SELECT status FROM pollster_health_status_hrpt20131 WHERE pollster_results_weekly_id ="+str(id)+""
        cursor.execute(sql)
        status = cursor.fetchone()[0]
        return status

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def is_unpublished(self):
        return self.status == 'UNPUBLISHED'

    @property
    def is_editable(self):
        return self.is_draft or self.is_unpublished

    @property
    def questions(self):
        for question in self.question_set.all():
            question.set_form(self.form)
            question.set_translation_survey(self.translation_survey)
            yield question

    @property
    def translation(self):
        return self.translation_survey

    # @models.permalink
    def get_absolute_url(self):
        return reverse('pollster_survey_edit', args=[str(self.id)])
        # return ('pollster_survey_edit', [str(self.id)])

    def __unicode__(self):
        return "Survey #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

    def get_table_name(self):
        if self.is_published and not self.shortname:
            raise RuntimeError('cannot generate tables for surveys with no shortname')
        return 'results_'+str(self.shortname)

    def get_last_participation_data(self, user_id, global_id):
        model = self.as_model()
        participation = model.objects\
            .filter(user=user_id)\
            .filter(global_id = global_id)\
            .order_by('-timestamp')\
            .values()
        return _get_or_default(participation)


    ####### IMPORTANT!!!! #####
    def as_model(self):
        fields = []
        if self.update:
            fields.extend(self._id_existing_field)

        fields.extend(self._standard_result_fields)

        for question in self.questions:
            fields += question.as_fields()
        model = dynamicmodels.create(self.get_table_name(), fields=dict(fields), app_label='pollster')
        return model


    def as_form(self):
        model = self.as_model()
        questions = list(self.questions)

        def clean(self):
            for q in questions:
                if self.cleaned_data.get(q.data_name) and q.is_text and q.data_type.title == "Text":
                    self.cleaned_data[q.data_name] = emoji.demojize(
                        self.cleaned_data[q.data_name], delimiters=EMOJI_DELIMITERS)
                for opt in q.options:
                    if opt.is_open and opt.open_option_data_type.title == "Text":
                        self.cleaned_data[opt.open_option_data_name] = emoji.demojize(
                            self.cleaned_data[opt.open_option_data_name], delimiters=EMOJI_DELIMITERS)

                if q.is_matrix_entry:
                    for row, cols in q.rows_columns:
                        for col in cols:
                            self.cleaned_data[col.data_name] = emoji.demojize(
                                self.cleaned_data[col.data_name], delimiters=EMOJI_DELIMITERS)

                if q.is_multiple_choice and q.is_mandatory:
                    valid = any([self.cleaned_data.get(d, False) for d in q.data_names])
                    if not valid:
                        self._errors[q.data_name] = self.error_class('At least one option should be selected')

                if (q.is_matrix_check or q.is_matrix_entry or q.is_matrix_select) and q.is_mandatory:
                    valid = all([self.cleaned_data.get(d, False) for d in q.data_names])
                    if not valid:
                        self._errors[q.data_name] = self.error_class("Some questions have not been answered")

            return self.cleaned_data

        form = dynamicmodels.to_form(model, {'clean': clean})

        for question in questions:
            if question.is_mandatory and question.data_name in form.base_fields:
                form.base_fields[question.data_name].required = True
        return form

    # I cannot for the love of me understand what value do such setters offer...
    def set_form(self, form):
        self.form = form

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey

    def get_errors(self):
        errors = []
        if not self.shortname:
            errors.append('Missing survey shortname')
        elif not re.match(IDENTIFIER_REGEX, self.shortname):
            errors.append('Invalid survey shortname "%s"' % (self.shortname,))

        data_names = self.question_set.values("data_name").annotate(
            nr=Count("data_name")).order_by().filter(nr__gt=1).values_list("data_name", flat=True)
        if data_names.exists():
            errors.append("Duplicate data name for " + ", ".join(["{}"]*data_names.count()).format(*data_names))

        for question in self.questions:
            errors.extend(question.get_errors())
        return errors

    def publish(self):
        if self.is_published:
            return None
        errors = self.get_errors()
        if not self.translationsurvey_set.filter(language="sv", status="PUBLISHED").exists():
            errors.append("Missing published `sv` translation survey for {}".format(self.shortname))
        if errors:
            return errors
        # Unpublish other surveys with the same shortname.
        for o in Survey.objects.filter(shortname=self.shortname, status='PUBLISHED'):
            o.unpublish()
        self.status = 'PUBLISHED'
        model = self.as_model()
        table = model._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            backup = table + '_vx_' + now.strftime('%Y%m%d%H%M%S')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        dynamicmodels.install(model)
        self.save()
        return None

    def unpublish(self):
        if not self.is_published:
            return
        table = self.as_model()._meta.db_table
        if table in connection.introspection.table_names():
            now = datetime.datetime.now()
            version = self.version or 0
            backup = table + '_v' + str(version) + '_' + now.strftime('%Y%m%d%H%M%S')
            connection.cursor().execute('ALTER TABLE '+table+' RENAME TO '+backup)
        self.status = 'UNPUBLISHED'
        self.save()

    def write_csv(self, writer, extra_fields=[]):
        def _get_fieldval_survery(obj, field_name):
            val = getattr(obj, field_name)
            if isinstance(val, str):
                val = emoji.emojize(val, delimiters=EMOJI_DELIMITERS)
            return val() if callable(val) else val

        model = self.as_model()
        field_names = [field.name for field in model._meta.fields]
        field_names.extend(extra_fields)
        writer.writerow(field_names)
        for result_row in model.objects.all():
            user = User.objects.get(id=result_row.user)
            # Exclude all staff and admin answers from the results
            if user.is_staff or user.is_superuser:
                continue

            id_code = SurveyIdCode.objects.get(surveyuser_global_id=result_row.global_id)
            row = [_get_fieldval_survery(result_row, field.name) for field in model._meta.fields]

            possible_extra_fields = {
                "email": user.email,
                "is_active": user.is_active,
                "id_code": id_code.idcode,
                "dob_from_idcode": id_code.fodelsedatum
            }

            for extra_field in extra_fields:
                row.append(possible_extra_fields[extra_field])

            writer.writerow(row)


@receiver(pre_delete, sender=Survey)
def pre_delete_survey(sender, instance, *args, **kwargs):
    # Clean up the survey group when the related Survey is deleted
    if instance.group:
        instance.group.delete()


class RuleType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "RuleType #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

class QuestionDataType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    db_type = models.CharField(max_length=255)
    css_class = models.CharField(max_length=255)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "QuestionDataType #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

    def as_field_type(self, verbose_name=None, regex=None):
        #really? just copy pasting code from the web without knowing what it does????
        import django.db.models
        import apps.pollster.db.models
        field = eval(self.db_type)
        field.verbose_name = verbose_name
        if regex:
            field.validators.append(RegexValidator(regex=regex))
        return field

    @staticmethod
    def default_type():
        return QuestionDataType.objects.filter(title = 'Text')[0]

    @staticmethod
    def default_timestamp_type():
        return QuestionDataType.objects.filter(title = 'Timestamp')[0]

    @property
    def is_internal(self):
        return self.title == 'Timestamp'

class VirtualOptionType(models.Model):
    title = models.CharField(max_length=255, blank=True, default='')
    question_data_type = models.ForeignKey(QuestionDataType, on_delete=models.CASCADE)
    js_class = models.CharField(max_length=255, unique=True)

    def __unicode__(self):
        return "VirtualOptionType #%d %s for %s" % (self.id, self.title, self.question_data_type.title)

    def __str__(self):
        return self.__unicode__()

class Question(models.Model):
    survey = models.ForeignKey(Survey, db_index=True, on_delete=models.CASCADE)
    starts_hidden = models.BooleanField(default=False)
    is_mandatory = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    type = models.CharField(max_length=255, choices=QUESTION_TYPE_CHOICES)
    data_type = models.ForeignKey(QuestionDataType, on_delete=models.CASCADE)
    open_option_data_type = models.ForeignKey(QuestionDataType, related_name="questions_with_open_option", null=True, blank=True, on_delete=models.CASCADE)
    data_name = models.CharField(max_length=40)
    visual = models.CharField(max_length=255, blank=True, default='')
    tags = models.CharField(max_length=255, blank=True, default='')
    regex = models.CharField(max_length=1023, blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    form = None
    translation_survey = None
    translation_question = None

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def translated_error_message(self):
        if self.translation and self.translation.error_message:
            return self.translation.error_message
        return self.error_message

    @property
    def errors(self):
        if not self.form:
            return {}

        errors = [(data_name, self.form.errors[data_name])
                  for data_name in self.data_names
                  if data_name in self.form.errors]

        if self.data_name in self.form.errors:
            if self.is_multiple_choice:
                errors.append((self.data_name, self.form.errors[self.data_name]))

            if self.is_matrix_check:
                errors.append((self.data_name, self.form.errors[self.data_name]))

            if self.is_matrix_select:
                errors.append((self.data_name, self.form.errors[self.data_name]))

            if self.is_matrix_entry:
                errors.append((self.data_name, self.form.errors[self.data_name]))

        return dict(errors)

    @property
    def rows(self):
        for row in self.row_set.all():
            row.set_translation_survey(self.translation_survey)
            yield row

    @property
    def columns(self):
        for column in self.column_set.all():
            column.set_translation_survey(self.translation_survey)
            yield column

    @property
    def rows_columns(self):
        for row in self.rows:
            yield (row, self._columns_for_row(row))

    def _columns_for_row(self, row):
        for column in self.columns:
            column.set_row(row)
            yield column

    @property
    def data_names(self):
        return [data_name for data_name, data_type in self.as_fields()]

    @property
    def options(self):
        for option in self.option_set.all():
            option.set_form(self.form)
            option.set_translation_survey(self.translation_survey)
            yield option

    @property
    def translation(self):
        return self.translation_question

    @property
    def css_classes(self):
        c = ['question', 'question-'+self.type, self.data_type.css_class]
        if self.starts_hidden:
            c.append('starts-hidden')
        if self.is_mandatory:
            c.append('mandatory')
        if self.errors:
            c.append('error')
        return c


    # This smells
    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')


    # So... after a zillion facepalms I think I cracked the mistery of the attack-of-the-@property-tag situation.
    # The motivation was to use these in the templates.
    # Here's an alternaitve: Read the f**in django documentation on template tags FFS!
    # or even better, stop picking a value from a list by manually if-ing every possivel value...?


    @property
    def is_builtin(self):
        return self.type == 'builtin'

    @property
    def is_text(self):
        return self.type == 'text'

    @property
    def is_single_choice(self):
        return self.type == 'single-choice'

    @property
    def is_multiple_choice(self):
        return self.type == 'multiple-choice'

    @property
    def is_matrix_select(self):
        return self.type == 'matrix-select'

    @property
    def is_matrix_entry(self):
        return self.type == 'matrix-entry'

    @property
    def is_matrix_check(self):
        return self.type == 'matrix-check'

    @property
    def is_visual_dropdown(self):
        return self.visual == 'dropdown'

    def __unicode__(self):
        return "Question #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ['survey', 'ordinal']

    def data_name_for_row_column(self, row, column):
        return '%s_multi_row%d_col%d' % (self.data_name, row.ordinal, column.ordinal)

    def as_fields(self):
        fields = []
        if self.type == 'builtin':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
        elif self.type == 'text':
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title, regex=self.regex)) ]
        elif self.type == 'single-choice':
            open_option_data_type = self.open_option_data_type or self.data_type
            fields = [ (self.data_name, self.data_type.as_field_type(verbose_name=self.title)) ]
            for open_option in [o for o in self.option_set.all() if o.is_open]:
                title_open = "%s: %s Open Answer" % (self.title, open_option.value)
                fields.append( (open_option.open_option_data_name, open_option_data_type.as_field_type(verbose_name=title_open)) )
        elif self.type == 'multiple-choice':
            fields = []
            for option in self.option_set.all():
                title = "%s: %s" % (self.title, option.value)
                fields.append( (option.data_name, models.BooleanField(verbose_name=title)) )
                if option.is_open:
                    title_open = "%s: %s Open Answer" % (self.title, option.value)
                    fields.append( (option.open_option_data_name, option.open_option_data_type.as_field_type(verbose_name=title_open)) )
        elif self.type in ('matrix-select', 'matrix-entry'):
            fields = []
            for row, columns in self.rows_columns:
                for column in columns:
                    r = row.title or ("row %d" % row.ordinal)
                    c = column.title or ("column %d" % column.ordinal)
                    title = "%s (%s, %s)" % (self.title, r, c)
                    fields.append( (column.data_name, self.data_type.as_field_type(verbose_name=title)) )
        elif self.type == "matrix-check":
            fields = []
            for row in self.rows:
                field_name = '%s_multi_row%d' % (self.data_name, row.ordinal)
                title = "%s (row %s)" % (self.title, row.ordinal)
                fields.append((field_name, self.data_type.as_field_type(verbose_name=title)))
        else:
            # Just because NotImplementedError looks badass or what?
            # I'll try to guess another reason why this would be here ... when I get bored
            raise NotImplementedError(self.type)
        return fields

    def set_form(self, form):
        self.form = form

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestion_set.all().filter(question=self)
            default = TranslationQuestion(translation = translation_survey, question=self)
            self.translation_question = _get_or_default(r, default)

    def get_errors(self):
        errors = []
        if not self.data_name:
            errors.append('Missing data name for question "%s"' % (self.title, ))
        elif not re.match(IDENTIFIER_REGEX, self.data_name):
            errors.append('Invalid data name "%s" for question "%s"' % (self.data_name, self.title))
        values = {}
        for option in self.options:
            errors.extend(option.get_errors())
            values[option.value] = values.get(option.value, 0) + 1
        if self.type == 'multiple-choice':
            dups = [val for val, count in values.items() if count > 1]
            for dup in dups:
                errors.append('Duplicated value %s in question %s' % (dup, self.title))
        return errors


class QuestionRow(models.Model):
    question = models.ForeignKey(Question, related_name="row_set", db_index=True, on_delete=models.CASCADE)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionRow #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_row

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestionrow_set.all().filter(row=self)
            default = TranslationQuestionRow(translation = translation_survey, row=self)
            self.translation_row = _get_or_default(r, default)

class QuestionColumn(models.Model):
    question = models.ForeignKey(Question, related_name="column_set", db_index=True, on_delete=models.CASCADE)
    ordinal = models.IntegerField()
    title = models.CharField(max_length=255, blank=True, default='')

    translation_survey = None
    translation_column = None
    row = None

    class Meta:
        ordering = ['question', 'ordinal']

    def __unicode__(self):
        return "QuestionColumn #%d %s" % (self.id, self.title)

    def __str__(self):
        return self.__unicode__()

    @property
    def translated_title(self):
        if self.translation and self.translation.title:
            return self.translation.title
        return self.title

    @property
    def translation(self):
        return self.translation_column

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationquestioncolumn_set.all().filter(column=self)
            default = TranslationQuestionColumn(translation = translation_survey, column=self)
            self.translation_column = _get_or_default(r, default)

    def set_row(self, row):
        self.row = row

    @property
    def options(self):
        for option in self.question.options:
            if option.row and option.row != self.row:
                continue
            if option.column and option.column != self:
                continue
            option.set_row_column(self.row, self)
            option.set_translation_survey(self.translation_survey)
            # TODO: We need a form to reset the selects to user's values.
            # option.set_form(self.form)
            yield option

    @property
    def data_name(self):
        if not self.row:
            raise NotImplementedError('use Question.rows_columns() to get the right data_name here')
        return self.question.data_name_for_row_column(self.row, self)

class Option(models.Model):
    question = models.ForeignKey(Question, db_index=True, on_delete=models.CASCADE)
    clone = models.ForeignKey('self', db_index=True, blank=True, null=True, on_delete=models.CASCADE)
    row = models.ForeignKey(QuestionRow, blank=True, null=True, on_delete=models.CASCADE)
    column = models.ForeignKey(QuestionColumn, blank=True, null=True, on_delete=models.CASCADE)
    is_virtual = models.BooleanField(default=False)
    is_open = models.BooleanField(default=False)
    starts_hidden = models.BooleanField(default=False)
    ordinal = models.IntegerField()
    text = models.CharField(max_length=4095, blank=True, default='')
    group = models.CharField(max_length=255, blank=True, default='')
    value = models.CharField(max_length=20, default='')
    description = models.TextField(blank=True, default='')

    virtual_type = models.ForeignKey(VirtualOptionType, blank=True, null=True, on_delete=models.CASCADE)
    virtual_inf = models.CharField(max_length=255, blank=True, default='')
    virtual_sup = models.CharField(max_length=255, blank=True, default='')
    virtual_regex = models.CharField(max_length=255, blank=True, default='')

    form = None
    translation_survey = None
    translation_option = None
    current_row_column = (None, None)

    @property
    def translated_text(self):
        if self.translation and self.translation.text:
            return self.translation.text
        return self.text

    @property
    def translated_description(self):
        if self.translation and self.translation.description:
            return self.translation.description
        return self.description

    @property
    def data_name(self):
        if self.question.type in ('text', 'single-choice'):
            return self.question.data_name
        elif self.question.type == 'multiple-choice':
            return self.question.data_name+'_'+self.value
        elif self.question.type in ('matrix-select', 'matrix-entry', 'matrix-check'):
            row = self.row or self.current_row_column[0]
            column = self.column or self.current_row_column[1]
            return self.question.data_name_for_row_column(row, column)
        else:
            raise NotImplementedError(self.question.type)

    @property
    def translation(self):
        return self.translation_option

    @property
    def open_option_data_name(self):
        return self.question.data_name+'_'+self.value+'_open'

    @property
    def open_option_data_type(self):
        return self.question.open_option_data_type or self.question.data_type

    def __unicode__(self):
        return 'Option #%d %s' % (self.id, self.value)

    def __str__(self):
        return self.__unicode__()

    class Meta:
        ordering = ['question', 'ordinal']

    @property
    def form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.data_name, '')

    @property
    def open_option_data_form_value(self):
        if not self.form:
            return ''
        return self.form.data.get(self.open_option_data_name, '')

    @property
    def form_is_checked(self):
        if self.question.type in ('text', 'single-choice'):
            return self.form_value == self.value
        elif self.question.type == 'multiple-choice':
            return bool(self.form_value)
        elif self.question.type in ('matrix-select', 'matrix-entry', 'matrix-check'):
            return self.form_value == self.value
        else:
            raise NotImplementedError(self.question.type)

    def set_form(self, form):
        self.form = form

    def set_translation_survey(self, translation_survey):
        self.translation_survey = translation_survey
        if translation_survey:
            r = translation_survey.translationoption_set.all().filter(option=self)
            default = TranslationOption(translation = translation_survey, option=self)
            self.translation_option = _get_or_default(r, default)

    def set_row_column(self, row, column):
        self.current_row_column = (row, column)

    def get_errors(self):
        errors = []
        if self.is_virtual:
            if not self.virtual_inf and not self.virtual_sup and not self.virtual_regex:
                errors.append('Missing parameters for derived value in question "%s"' % (self.question.title, ))
        else:
            if not self.text:
                errors.append('Empty text for option in question "%s"' % (self.question.title, ))
            if not self.value:
                errors.append('Missing value for option "%s" in question "%s"' % (self.text, self.question.title))
            elif self.question.type == 'multiple-choice' and not re.match(IDENTIFIER_OPTION_REGEX, self.value):
                errors.append('Invalid value "%s" for option "%s" in question "%s"' % (self.value, self.text, self.question.title))
        return errors

class Rule(models.Model):
    rule_type = models.ForeignKey(RuleType, on_delete=models.CASCADE)
    is_sufficient = models.BooleanField(default=True)
    subject_question = models.ForeignKey(Question, related_name='subject_of_rules', db_index=True, on_delete=models.CASCADE)
    subject_options = models.ManyToManyField(Option, related_name='subject_of_rules', limit_choices_to={'question': subject_question})
    object_question = models.ForeignKey(Question, related_name='object_of_rules', blank=True, null=True, on_delete=models.CASCADE)
    object_options = models.ManyToManyField(Option, related_name='object_of_rules', limit_choices_to={'question': object_question})

    def js_class(self):
        return self.rule_type.js_class

    def __unicode__(self):
        return 'Rule #%d' % (self.id)

    def __str__(self):
        return self.__unicode__()

# I18n models

class TranslationSurvey(models.Model):
    survey = models.ForeignKey(Survey, db_index=True, on_delete=models.CASCADE)
    language = models.CharField(max_length=3, db_index=True)
    title = models.CharField(max_length=255, blank=True, default='')
    status = models.CharField(max_length=255, default='DRAFT', choices=SURVEY_TRANSLATION_STATUS_CHOICES)

    class Meta:
        verbose_name = 'Translation'
        ordering = ['survey', 'language']
        unique_together = ('survey', 'language')

    # @models.permalink
    def get_absolute_url(self):
        # return ('pollster_survey_translation_edit', [str(self.survey.id), self.language])
        return reverse('pollster_survey_translation_edit', args=[str(self.survey.id), self.language])

    def __unicode__(self):
        return "TranslationSurvey(%s) for %s" % (self.language, self.survey)

    def __str__(self):
        return self.__unicode__()

    def as_form(self, data=None):
        class TranslationSurveyForm(ModelForm):
            class Meta:
                model = TranslationSurvey
                fields = ['title', 'status']
        return TranslationSurveyForm(data, instance=self, prefix="survey")

class TranslationQuestion(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, db_index=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, default='')
    description = models.TextField(blank=True, default='')
    error_message = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'question']
        unique_together = ('translation', 'question')

    def __unicode__(self):
        return "TranslationQuestion(%s) for %s" % (self.translation.language, self.question)

    def __str__(self):
        return self.__unicode__()

    def as_form(self, data=None):
        class TranslationQuestionForm(ModelForm):
            class Meta:
                model = TranslationQuestion
                fields = ['title', 'description', 'error_message']
        return TranslationQuestionForm(data, instance=self, prefix="question_%s"%(self.id,))

class TranslationQuestionRow(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True, on_delete=models.CASCADE)
    row = models.ForeignKey(QuestionRow, db_index=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'row']
        unique_together = ('translation', 'row')

    def __unicode__(self):
        return "TranslationQuestionRow(%s) for %s" % (self.translation.language, self.row)

    def __str__(self):
        return self.__unicode__()

    def as_form(self, data=None):
        class TranslationRowForm(ModelForm):
            class Meta:
                model = TranslationQuestionRow
                fields = ['title']
        return TranslationRowForm(data, instance=self, prefix="row_%s"%(self.id,))

class TranslationQuestionColumn(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True, on_delete=models.CASCADE)
    column = models.ForeignKey(QuestionColumn, db_index=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, default='')

    class Meta:
        ordering = ['translation', 'column']
        unique_together = ('translation', 'column')

    def __unicode__(self):
        return "TranslationQuestionColumn(%s) for %s" % (self.translation.language, self.column)

    def __str__(self):
        return self.__unicode__()

    def as_form(self, data=None):
        class TranslationColumnForm(ModelForm):
            class Meta:
                model = TranslationQuestionColumn
                fields = ['title']
        return TranslationColumnForm(data, instance=self, prefix="column_%s"%(self.id,))

class TranslationOption(models.Model):
    translation = models.ForeignKey(TranslationSurvey, db_index=True, on_delete=models.CASCADE)
    option = models.ForeignKey(Option, db_index=True, on_delete=models.CASCADE)
    text = models.CharField(max_length=4095, blank=True, default='')
    description = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['translation', 'option']
        unique_together = ('translation', 'option')

    def __unicode__(self):
        return "TranslationOption(%s) for %s" % (self.translation.language, self.option)

    def __str__(self):
        return self.__unicode__()

    def as_form(self, data=None):
        class TranslationOptionForm(ModelForm):
            class Meta:
                model = TranslationOption
                fields = ['text', 'description']
        return TranslationOptionForm(data, instance=self, prefix="option_%s"%(self.id,))

class ChartType(models.Model):
    shortname = models.SlugField(max_length=255, unique=True)
    description = models.CharField(max_length=255)

    def __unicode__(self):
        return self.description or self.shortname

    def __str__(self):
        return self.__unicode__()

class Chart(models.Model):
    survey = models.ForeignKey(Survey, db_index=True, on_delete=models.CASCADE)
    type = models.ForeignKey(ChartType, db_index=True, on_delete=models.CASCADE)
    shortname = models.SlugField(max_length=255)
    chartwrapper = models.TextField(blank=True, default='')
    sqlsource = models.TextField(blank=True, default='', verbose_name="SQL Source Query")
    sqlfilter = models.CharField(max_length=255, default='NONE', choices=CHART_SQLFILTER_CHOICES, verbose_name="Results Filter")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=255, default='DRAFT', choices=CHART_STATUS_CHOICES)
    geotable = models.CharField(max_length=255, default='pollster_zip_codes', choices=settings.GEOMETRY_TABLES)

    class Meta:
        ordering = ['survey', 'shortname']
        unique_together = ('survey', 'shortname')

    def __unicode__(self):
        return "Chart %s for %s" % (self.shortname, self.survey)

    def __str__(self):
        return self.__unicode__()

    # @models.permalink
    def get_absolute_url(self):
        # return ('pollster_survey_chart_edit', [str(self.survey.id), self.shortname])
        return reverse('pollster_survey_chart_edit', args=[str(self.survey.id), self.shortname])

    @property
    def is_draft(self):
        return self.status == 'DRAFT'

    @property
    def is_published(self):
        return self.status == 'PUBLISHED'

    @property
    def has_data(self):
        if not self.sqlsource:
            return False
        else:
            return True

    # Pretty sure, just by looking at graphical mass of uninteligeable code,
    # that this method does more than 'to_json'.How difficult can it be, really
    def to_json(self, user_id, global_id):
        data = {}
        if self.type.shortname == "google-charts":
            data[ "chartType"] = "Table"
            if self.chartwrapper:
                data = json.loads(self.chartwrapper)
            descriptions, cells = self.load_data(user_id, global_id)
            cols = [{"id": desc[0], "label": desc[0], "type": "number"} for desc in descriptions]
            rows = [{"c": [{"v": v} for v in c]} for c in cells]
            data["dataTable"] = { "cols": cols, "rows": rows }

        else:
            if self.chartwrapper:
                data["bounds"] = json.loads(self.chartwrapper)
            try:
                shortname = settings.POLLSTER_USER_PROFILE_SURVEY
                survey = Survey.objects.get(shortname=shortname, status='PUBLISHED')
                lpd = survey.get_last_participation_data(user_id, global_id)
                if lpd and hasattr(settings, 'POLLSTER_USER_ZIP_CODE_DATA_NAME'):
                    zip_code = lpd.get(settings.POLLSTER_USER_ZIP_CODE_DATA_NAME)
                    if zip_code is not None:
                        zip_code = str(zip_code).upper()
                    country = None
                    if hasattr(settings, 'POLLSTER_USER_COUNTRY_DATA_NAME'):
                        country = lpd.get(settings.POLLSTER_USER_COUNTRY_DATA_NAME)
                        if country is not None:
                            country = str(country).upper()
                    data["center"] = self.load_zip_coords(zip_code, country)
            except:
                # really? The old school except pass?... ok then
                pass

        return json.dumps(data)

    def get_map_click(self, lat, lng):
        result = {}
        skip_cols = ("ogc_fid", "color", "geometry")
        description, data = self.load_info(lat, lng)
        if data and len(data) > 0:
            for i in range(len(data[0])):
                if description[i][0] not in skip_cols:
                    result[description[i][0]] = str(data[0][i])
        return json.dumps(result)

    def get_map_tile(self, user_id, global_id, z, x, y):
        filename = self.get_map_tile_filename(z, x, y)
        if self.sqlfilter == "USER" and user_id:
            filename = filename + "_user_" + str(user_id)
        elif self.sqlfilter == "PERSON" and global_id:
            filename = filename + "_gid_" + global_id
        if not os.path.exists(filename):
            self.generate_map_tile(self.generate_mapnik_map(user_id, global_id), filename, z, x, y)
        return open(filename).read()

    def generate_map_tile(self, m, filename, z, x, y):
        # Code taken from OSM generate_tiles.py
        proj = GoogleProjection()
        mprj = mapnik.Projection(m.srs)

        p0 = (x * 256, (y + 1) * 256)
        p1 = ((x + 1) * 256, y * 256)
        l0 = proj.fromPixelToLL(p0, z);
        l1 = proj.fromPixelToLL(p1, z);
        c0 = mprj.forward(mapnik.Coord(l0[0], l0[1]))
        c1 = mprj.forward(mapnik.Coord(l1[0], l1[1]))

        if hasattr(mapnik,'mapnik_version') and mapnik.mapnik_version() >= 800:
            bbox = mapnik.Box2d(c0.x, c0.y, c1.x, c1.y)
        else:
            bbox = mapnik.Envelope(c0.x, c0.y, c1.x, c1.y)

        m.resize(256, 256)
        m.zoom_to_box(bbox)

        im = mapnik.Image(256, 256)
        mapnik.render(m, im)
        # See https://github.com/mapnik/mapnik/wiki/OutputFormats for output
        # formats and special parameters. The default here is 32 bit PNG with 8
        # bit per component and alpha channel.
        if mapnik_version == 2:
            im.save(str(filename), "png32")
        else:
            im.save(str(filename), "png")

    def generate_mapnik_map(self, user_id, global_id):
        m = mapnik.Map(256, 256)

        style = self.generate_mapnik_style(user_id, global_id)

        m.background = mapnik.Color("transparent")
        m.append_style("ZIP_CODES STYLE", style)
        m.srs = "+proj=merc +a=6378137 +b=6378137 +lat_ts=0.0 +lon_0=0.0 +x_0=0.0 +y_0=0 +k=1.0 +units=m +nadgrids=@null +no_defs +over"

        layer = mapnik.Layer('ZIP_CODES')
        layer.datasource = self.create_mapnik_datasource(user_id, global_id)
        layer.styles.append("ZIP_CODES STYLE")
        m.layers.append(layer)

        return m

    def generate_mapnik_style(self, user_id, global_id):
        style = mapnik.Style()
        for color in self.load_colors(user_id, global_id):
            # If the color can't be parsed, use red.
            try:
                c = mapnik.Color(str(color))
            except:
                c = mapnik.Color('#ff0000')
            line = mapnik.LineSymbolizer(c, 1.5)
            line.stroke.opacity = 0.7
            poly = mapnik.PolygonSymbolizer(c)
            poly.fill_opacity = 0.5
            rule = mapnik.Rule()
            rule.filter = mapnik.Filter(str("[color] = '%s'" % (color,)))
            rule.symbols.extend([poly,line])
            style.rules.append(rule)
        return style

    def create_mapnik_datasource(self, user_id, global_id):
        # First create the SQL query that is a join between pollster_zip_codes and
        # the chart query as created by the user; then create an appropriate datasource.

        if global_id and re.findall('[^0-9A-Za-z-]', global_id):
            raise Exception("invalid global_id "+global_id)

        table = """SELECT * FROM %s""" % (self.get_view_name(),)
        if self.sqlfilter == 'USER' :
            table += """ WHERE "user" = %d""" % (user_id,)
        elif self.sqlfilter == 'PERSON':
            table += """ WHERE "user" = %d AND global_id = '%s'""" % (user_id, global_id)
        table = "(" + table + ") AS ZIP_CODES"

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.sqlite3":
            name = settings.DATABASES["default"]["NAME"]
            return mapnik.SQLite(file=filename, wkb_format="spatialite",
                geometry_field="geometry", estimate_extent=False, table=table)

        if settings.DATABASES["default"]["ENGINE"] == "django.db.backends.postgresql_psycopg2":
            name = settings.DATABASES["default"]["NAME"]
            host = settings.DATABASES["default"]["HOST"]
            port = settings.DATABASES["default"]["PORT"]
            username = settings.DATABASES["default"]["USER"]
            password = settings.DATABASES["default"]["PASSWORD"]
            return mapnik.PostGIS(host=host, port=port, user=username, password=password, dbname=name,
                geometry_field="geometry", estimate_extent=False, table=table)

    def get_map_tile_base(self):
        return "%s/_pollster_tile_cache/survey_%s/%s" % (settings.POLLSTER_CACHE_PATH, self.survey.id, self.shortname)

    def get_map_tile_filename(self, z, x, y):
        filename = "%s/%s/%s_%s" % (self.get_map_tile_base(), z, x, y)
        pathname = os.path.dirname(filename)
        if not os.path.exists(pathname):
            try:
                os.makedirs(pathname)
            except OSError:
                # Another thread created the directory in the meantime: just go on.
                pass
        return filename

    def clear_map_tile_cache(self):
        try:
            shutil.rmtree(self.get_map_tile_base())
        except:
            pass

    def get_table_name(self):
        return 'pollster_charts_'+str(self.survey.shortname)+'_'+str(self.shortname)

    def get_view_name(self):
        return self.get_table_name() + "_view"

    def update_table(self):
        table_query = self.sqlsource
        geo_table = self.geotable
        if table_query:
            table = self.get_table_name()
            view = self.get_view_name()
            # So what we do next is determined by a regex search on an SQL we wrote somewhere...
            # I'm not sure one can continue reading this without the risk of serious psicological health consequences
            if re.search(r'\bzip_code_country\b', table_query):
                view_query = """SELECT A.*, B.id AS OGC_FID, B.geometry
                                  FROM %s B, (SELECT * FROM %s) A
                                 WHERE upper(A.zip_code_key) = upper(B.zip_code_key)
                                   AND upper(A.zip_code_country) = upper(B.country)""" % (geo_table, table,)
            else:
                view_query = """SELECT A.*, B.id AS OGC_FID, B.geometry
                                  FROM %s B, (SELECT * FROM %s) A
                                 WHERE upper(A.zip_code_key) = upper(B.zip_code_key)""" % (geo_table, table,)
            cursor = connection.cursor()
            cursor.execute("DROP VIEW IF EXISTS %s" % (view,))
            cursor.execute("DROP TABLE IF EXISTS %s" % (table,))
            cursor.execute("CREATE TABLE %s AS %s" % (table, table_query))
            if self.type.shortname != 'google-charts':
                cursor.execute("CREATE VIEW %s AS %s" % (view, view_query))
            transaction.commit_unless_managed()
            self.clear_map_tile_cache()
            return True
        return False

    def update_data(self):
        table_query = self.sqlsource
        if table_query:
            table = self.get_table_name()
            cursor = connection.cursor()
            try:
                cursor.execute("DELETE FROM %s" % (table,))
                cursor.execute("INSERT INTO %s %s" % (table, table_query))
                transaction.commit_unless_managed()
                self.clear_map_tile_cache()
                return True
            except IntegrityError:
                return False
            except DatabaseError:
                return False
        return False

    def load_data(self, user_id, global_id):
        table = self.get_table_name()
        query = "SELECT * FROM %s" % (table,)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return (cursor.description, cursor.fetchall())
        except DatabaseError as e:
            return ((('Error',),), ((str(e),),))

    def load_colors(self, user_id, global_id):
        table = self.get_table_name()
        query = """SELECT DISTINCT color FROM %s""" % (table,)
        if self.sqlfilter == 'USER' :
            query += """ WHERE "user" = %(user_id)s"""
        elif self.sqlfilter == 'PERSON':
            query += """ WHERE "user" = %(user_id)s AND global_id = %(global_id)s"""
        params = { 'user_id': user_id, 'global_id': global_id }
        try:
            cursor = connection.cursor()
            cursor.execute(query, params)
            return [x[0] for x in cursor.fetchall()]
        except DatabaseError as e:
            # If the SQL query is wrong we just return 'red'. We don't try to pop
            # up a warning because this probably is an async Javascript call: the
            # query error should be shown by the map editor.
            return ['#ff0000']

    def load_info(self, lat, lng):
        view = self.get_view_name()
        query = "SELECT * FROM %s WHERE ST_Contains(geometry, 'SRID=4326;POINT(%%s %%s)')" % (view,)
        try:
            cursor = connection.cursor()
            cursor.execute(query, (lng, lat))
            return (cursor.description, cursor.fetchall())
        except DatabaseError as e:
            return (None, [])

    def load_zip_coords(self, zip_code_key, zip_code_country=None):
        geo_table = self.geotable
        if zip_code_country:
            query = """SELECT ST_Y(ST_Centroid(geometry)) AS lat, ST_X(ST_Centroid(geometry)) AS lng
                         FROM """ + geo_table + """ WHERE zip_code_key = %s AND country = %s"""
            args = (zip_code_key, zip_code_country)

        else:
            query = """SELECT ST_Y(ST_Centroid(geometry)) AS lat, ST_X(ST_Centroid(geometry)) AS lng
                         FROM """ + geo_table + """ WHERE zip_code_key = %s"""
            args = (zip_code_key,)
        try:
            cursor = connection.cursor()
            cursor.execute(query, args)
            data = cursor.fetchall()
            if len(data) > 0:
                return {"lat": data[0][0], "lng": data[0][1]}
            else:
                return {}
        except DatabaseError as e:
            return {}

class GoogleProjection:
    def __init__(self, levels=25):
        self.Bc = []
        self.Cc = []
        self.zc = []
        self.Ac = []
        c = 256
        for d in range(0,levels):
            e = c/2;
            self.Bc.append(c/360.0)
            self.Cc.append(c/(2 * pi))
            self.zc.append((e,e))
            self.Ac.append(c)
            c *= 2

    def fromLLtoPixel(self,ll,zoom):
         d = self.zc[zoom]
         e = round(d[0] + ll[0] * self.Bc[zoom])
         f = min(max(sin(DEG_TO_RAD * ll[1]),-0.9999),0.9999)
         g = round(d[1] + 0.5*log((1+f)/(1-f))*-self.Cc[zoom])
         return (e,g)

    def fromPixelToLL(self,px,zoom):
         e = self.zc[zoom]
         f = (px[0] - e[0])/self.Bc[zoom]
         g = (px[1] - e[1])/-self.Cc[zoom]
         h = RAD_TO_DEG * ( 2 * atan(exp(g)) - 0.5 * pi)
         return (f,h)


class SurveyChartPlugin(CMSPlugin):
    chart = models.ForeignKey(Chart, on_delete=models.CASCADE)


class ZipCodes(models.Model):
    country = models.TextField()
    zip_code_key = models.TextField()
    geometry = MultiPolygonField()
