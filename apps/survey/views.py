# -*- coding: utf-8 -*-
from datetime import datetime
import json
import logging

from django import forms
from django.db import OperationalError
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.utils.translation import get_language
from django.conf import settings

from apps.pollster.models import TranslationSurvey, Survey
from apps.pollster import fields as pollser_field_types
from apps.survey.forms import AddPeople
from apps.survey.models import SurveyResponseDraft, SurveyIdCode, SurveyUser


logger = logging.getLogger(__name__)


def _get_active_survey_user(request):
    """
    Currently the system only allows one respondent (surveyuser) per user.
    Therefore, each user is only mapped to one survey user and the active
    surveyuser is that only user.

    If the system should be extended to support multiple respondents, this
    method should be refactored to return the selected active respondent.
    """
    return request.user.surveyuser_set.first()


@login_required
def select_survey_user(request, template='survey/select_user.html'):
    next = request.GET.get('next', None)
    if next is None:
        next = '/'

    users = SurveyUser.objects.filter(user=request.user, deleted=False)
    total = len(users)
    if total == 1:
        survey_user = users[0]
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)

    return render(request, template, {
        'users': users,
        'next': next,
    })


@login_required
def show_survey(request, survey_short_name):

    #Saving the response drafts so the users don't loose their replies
    #this should be put in its own route
    if "draft" in request.GET and request.method == 'POST':
        _save_survey_response_draft(request)
        return HttpResponse("Form state saved")

    # until we update to django 1.8, get_language() will allways return LANGUAGE_CODE
    # which is defined in the settings. But the best at this point, is removing translations altogether
    language = get_language()

    #locale_code = locale.locale_alias.get(language)

    survey_queryset = Survey.objects.filter(
        shortname=survey_short_name,
        status="PUBLISHED"
    )

    if survey_queryset.count() == 0:
        raise Http404

    survey_queryset = survey_queryset.prefetch_related(
        'question_set',
        'question_set__option_set',
        'question_set__option_set__virtual_type',
        'question_set__column_set',
        'question_set__row_set',
        'question_set__subject_of_rules',
        'question_set__subject_of_rules__subject_options',
        'question_set__subject_of_rules__object_options',
        'question_set__subject_of_rules__object_question',
        'question_set__subject_of_rules__rule_type',
        'question_set__data_type',
    )

    survey = survey_queryset.first()

    translation = TranslationSurvey.objects.get(
        survey=survey,
        language=language,
        status="PUBLISHED"
    )

    survey.set_translation_survey(translation)

    survey_user = _get_active_survey_user(request)
    global_id = survey_user.global_id

    # Check if the user has access to the survey
    if not survey.has_access(request.user):
        return HttpResponseRedirect("/sv/valkommen/")

    # Redirect the user if the intake survey has not been answered
    if survey.shortname != "intake":
        try:
            intake = Survey.objects.get(shortname="intake", status="PUBLISHED")
        except Survey.DoesNotExist:
            intake = None

        # Redirect is there exists a published intake survey and the user has not answered it
        if intake and not intake.get_last_participation_data(request.user.id, global_id):
            return HttpResponseRedirect("/sv/valkommen/")

    if survey.get_last_participation_data(request.user.id, global_id):
        return HttpResponseRedirect('/already-answered')

    id_code = get_object_or_404(
        SurveyIdCode,
        surveyuser_global_id=global_id
    )

    try:
        survey_response_draft = SurveyResponseDraft.objects.get(
            survey_user=survey_user,
            survey=survey
        )
        prefilled_data = json.loads(survey_response_draft.form_data)
    except SurveyResponseDraft.DoesNotExist:
        prefilled_data = {}

    # we inject the birthyear that was provided with the idcode so we know how old
    # the user is. There must be a question with this name in the survey for this to be usable
    # tipically it would be set to hidden.
    prefilled_data['PREFIL_BIRTHYEAR'] = id_code.fodelsedatum

    form = survey.as_form()(prefilled_data)

    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = request.user.id
        data['global_id'] = global_id
        data['timestamp'] = datetime.now()

        form = survey.as_form()(data)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/sv/valkommen/')
        else:
            survey.set_form(form)

            # Add the form to the question in order for the question to
            # retrieve validation errors in the template
            for question in survey.question_set.all():
                question.set_form(form)

    return render(
        request,
        'survey_run.html',
        {
            "language": language,
            "locale_code": "sv-SE", # let's just hardcode this for now
            "survey": survey,
            "default_postal_code_format": pollser_field_types.PostalCodeField.get_default_postal_code_format(),
            "last_participation_data_json": json.dumps(prefilled_data),
            "form": form,
            "person": survey_user,
            "settings": settings,
        },
    )


def _save_survey_response_draft(request):
    raw_data = json.loads(request.body.decode("utf-8"))
    survey_id = raw_data['survey_id']
    questions_data = raw_data['form_data']

    survey_user = _get_active_survey_user(request)

    try:
        SurveyResponseDraft.objects.update_or_create(
            survey_user=survey_user,
            survey_id=survey_id,
            defaults={
                'form_data': json.dumps(questions_data)
            }
        )
    except OperationalError as oe:
        # In case we face a MySQL deadlock (error code 1213), log a notice and
        # skip saving this draft.
        error_code, _ = oe.args

        if error_code == 1213:
            logger.warning('Deadlock while saving draft. Skipping draft save.')
        else:
            raise


# end of [relatively] sane code.
# ------------------------------------------------------------------------------


#The code from here on, is for managing multiple people with the same account
# something we don't use anymore and realistically speaking, would be too much
# work to pull back this undocumented and possibly unfinished code  back to life.

#TODO: remove from here on. Of course, this includes removing urls routes and such

@login_required
def people_edit(request):
    try:
        survey_user = _get_active_survey_user(request)
    except ValueError:
        raise Http404()
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_survey_user), reverse(people_edit))
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    if request.method == 'POST':
        form = AddPeople(request.POST)
        if form.is_valid():
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            return HttpResponseRedirect(reverse(people))
    else:
        form = forms.AddPeople(initial={'name': survey_user.name})

    return render_to_response('people_edit.html', {'base_template': "base.html",'form': form},
                              context_instance=RequestContext(request))



@login_required
def people_remove(request):
    try:
        survey_user = _get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = reverse(people)
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    confirmed = request.POST.get('confirmed', None)

    if confirmed == 'Y':
        survey_user.deleted = True
        survey_user.save()

        url = reverse(people)
        return HttpResponseRedirect(url)

    elif confirmed == 'N':
        url = reverse(people)
        return HttpResponseRedirect(url)

    else:
        return render_to_response('people_remove.html', {'person': survey_user},
                              context_instance=RequestContext(request))

@login_required
def people_add(request):
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user = SurveyUser()
            survey_user.user = request.user
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            messages.add_message(request, messages.INFO,
                _('A new person has been added.'))

            next = request.GET.get('next', None)
            if next is None:
                url = reverse(people)
            else:
                url = '%s?gid=%s' % (next, survey_user.global_id)
            return HttpResponseRedirect(url)

    else:
        form = forms.AddPeople()

    return render_to_response('people_add.html', {'form': form},
                              context_instance=RequestContext(request))

@login_required
def people(request):
    return HttpResponseRedirect(reverse(thanks))
