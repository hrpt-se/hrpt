# -*- coding: utf-8 -*-
import json

from django.core.urlresolvers import get_resolver, reverse, RegexURLResolver
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import to_locale, get_language
from django.template import RequestContext
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login
from django.conf import settings

from apps.survey.models import SurveyUser, SurveyIdCode
from .utils import get_user_profile
from . import models, forms, fields, parser, importexport
import re, datetime, locale, csv, urlparse, urllib
import sys



def render_with_context(req, *args, **kwargs):
    """
    So why is this in here? why do we need this method?
    Apparently no one knows. This method was here when I took over this codebase

    This was obviously added to prevent this error:
    > You must enable the 'sekizai.context_processors.sekizai'

    Now, what that means, why it occurs and why we need to manually set the context as a kwarg, is a whole other story.
    For now let's just rename this function to something a bit more descriptive.
    Naming this 'request_render_to_response', which was the previouns name, is either trolling or obfuscation

    https://github.com/django-compressor/django-compressor/issues/483#issuecomment-52243164
    """
    # kwargs['context_instance'] = RequestContext(req)
    return render(req, *args, **kwargs)


#This stuff is ... intense
# get rid of it!
#From here....

#EDIT: only one function left... we're getting there!!!!

def retry(f, *args, **kwargs):
    tries = 2
    while tries:
        try:
            return f(*args, **kwargs)
        except:
            tries -= 1
            if tries == 0:
                raise

# ... until here!


@staff_member_required
def survey_list(request):
    surveys = models.Survey.objects.all()
    form_import = forms.SurveyImportForm()
    return render_with_context(request, 'pollster/survey_list.html', {
        "surveys": surveys,
        "form_import": form_import
    })

@staff_member_required
def survey_add(request):
    survey = models.Survey()
    if (request.method == 'POST'):
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            # create and redirect
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    # return an empty survey structure
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return render_with_context(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_edit(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if not survey.is_editable:
        return redirect(survey_test, id=id)
    if request.method == 'POST':
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return render_with_context(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_publish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        errors = survey.publish()
        if errors:
            messages.error(request, 'Unable to publish the survey, please check the errors below')
            for error in errors[:5]:
                messages.warning(request, error)
        return redirect(survey)
    return redirect(survey)

@staff_member_required
def survey_unpublish(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        survey.unpublish()
        return redirect(survey)
    return redirect(survey)


@staff_member_required
def survey_test(request, id, language=None):
    survey_queryset = models.Survey.objects.all().prefetch_related(
        'question_set'
    )

    survey = get_object_or_404(survey_queryset, pk=id)

    #Notice that the language parameter passed to this as a url paramter _is ignored!_
    #TODO hardcode language, update urls, remove language paramter on this method
    language = get_language()
    translation = models.TranslationSurvey.objects.get(survey=survey, language=language)

    survey.set_translation_survey(translation)

    survey_user = SurveyUser.objects.get(user=request.user)
    IdCodeObject = get_object_or_404(SurveyIdCode, surveyuser_global_id=survey_user.global_id)
    prefilled_data = {"PREFIL_BIRTHYEAR": IdCodeObject.fodelsedatum}
    form = None

    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = request.user.id
        data['global_id'] = survey_user.global_id
        data['timestamp'] = datetime.datetime.now()
        form = survey.as_form()(data)

        #TODO: probably want to remove this next url crap
        if form.is_valid():
            if language:
                next_url = _get_next_url(request, reverse(survey_test, kwargs={'id':id, 'language': language}))
            else:
                next_url = _get_next_url(request, reverse(survey_test, kwargs={'id':id}))
            return HttpResponseRedirect(next_url)
        else:
            survey.set_form(form)

            # Add the form to the question in order for the question to
            # retrieve validation errors in the template
            for question in survey.question_set.all():
                question.set_form(form)

    return render(request, 'pollster/survey_test.html', {
        "language": language,
        "locale_code": "sv-SE", #TODO: oh well... remove internationalization
        "survey": survey,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "last_participation_data_json": json.dumps(prefilled_data),
        "form": form
    })


@staff_member_required
def survey_translation_list_or_add(request, id):
    #TODO: refactor this... python pyramids of doom only take half the work to refactor! we're lucky!
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyTranslationAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyTranslationAddForm(request.POST)
        if form_add.is_valid():
            language = form_add.cleaned_data['language']
            translations = survey.translationsurvey_set.all().filter(language=language)[0:1]
            if translations:
                translation = translations[0]
            else:
                translation = models.TranslationSurvey(survey=survey, language=language)
                survey.set_translation_survey(translation)
                survey.translation_survey.save()
                for question in survey.questions:
                    question.translation_question.save()
                    for option in question.options:
                        option.translation_option.save()
                    for row in question.rows:
                        row.translation_row.save()
                    for column in question.columns:
                        column.translation_column.save()

            return redirect(translation)
    return render_with_context(request, 'pollster/survey_translation_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_translation_edit(request, id, language):
    survey = get_object_or_404(models.Survey, pk=id)
    translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
    survey.set_translation_survey(translation)
    if request.method == 'POST':
        forms = []
        forms.append( survey.translation.as_form(request.POST) )
        for question in survey.questions:
            forms.append( question.translation.as_form(request.POST) )
            for row in question.rows:
                forms.append( row.translation.as_form(request.POST) )
            for column in question.columns:
                forms.append( column.translation.as_form(request.POST) )
            for option in question.options:
                forms.append( option.translation.as_form(request.POST) )
        if all(f.is_valid() for f in forms):
            for form in forms:
                form.save()
            messages.success(request, 'Translation saved successfully.')
            return redirect(translation)
    return render_with_context(request, 'pollster/survey_translation_edit.html', {
        "survey": survey,
        "translation": translation
    })

@staff_member_required
def survey_chart_list_or_add(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyChartAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyChartAddForm(request.POST)
        if form_add.is_valid():
            shortname = form_add.cleaned_data['shortname']
            charts = survey.chart_set.all().filter(shortname=shortname)[0:1]
            if charts:
                chart = charts[0]
            else:
                chart = models.Chart(survey=survey, shortname=shortname)
                chart.type = models.ChartType.objects.all().order_by('id')[0]
                chart.save()
            return redirect(chart)
    return render_with_context(request, 'pollster/survey_chart_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_chart_edit(request, id, shortname):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    form_chart = forms.SurveyChartEditForm(instance=chart)
    if request.method == 'POST':
        form_chart = forms.SurveyChartEditForm(request.POST, instance=chart)
        if form_chart.is_valid():
            form_chart.save()
            if not chart.update_table():
                msg = 'Unable to gather some data. Please check the SQL statements.'
                if chart.is_published:
                    messages.error(request, msg)
                else:
                    messages.warning(request, msg)
            return redirect(chart)
    return render_with_context(request, 'pollster/survey_chart_edit.html', {
        "survey": survey,
        "chart": chart,
        "form_chart": form_chart,
    })

@staff_member_required
def survey_chart_data(request, id, shortname):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

@staff_member_required
def survey_chart_map_tile(request, id, shortname, z, x, y):
    if int(z) > 22:
        raise Http404
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

@staff_member_required
def survey_chart_map_click(request, id, shortname, lat, lng):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

@staff_member_required
def survey_results_csv(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    now = datetime.datetime.now()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename=survey-results-%d-%s.csv' % (survey.id, format(now, '%Y%m%d%H%M'))
    response.write(u'\ufeff'.encode('utf8'))
    writer = csv.writer(response)
    survey.write_csv(writer)
    return response

@staff_member_required
def survey_results_csv_extended(request, id):
    #TODO: initialize the form variable here, later assign its contents if the request is post
    survey = get_object_or_404(models.Survey, pk=id)
    if request.method == 'POST': # If the form has been submitted...
        form = forms.SurveyExtendedResultsForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            # Process the data in form.cleaned_data
            now = datetime.datetime.now()
            response = HttpResponse(mimetype='text/csv')
            response['Content-Disposition'] = 'attachment; filename=survey-results-%d-%s.csv' % (survey.id, format(now, '%Y%m%d%H%M'))
            response.write(u'\ufeff'.encode('utf8'))
            #side effecting the response... great...
            writer = csv.writer(response)
            survey.write_csv(writer, extra_fields = form.cleaned_data)
            return response

    else:
        #http://stackoverflow.com/questions/5263722/in-django-how-do-i-late-bind-an-unbound-form
        form = forms.SurveyExtendedResultsForm() # An unbound form

    return render_to_response('pollster/extended_results.html', {
        'form': form,
        'survey': survey,
    }, context_instance=RequestContext(request))


@staff_member_required
def survey_export(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    serialized_survey = importexport.survey_to_json(survey)
    response = HttpResponse(serialized_survey, content_type="application/json")
    response['Content-Disposition'] = 'attachment; filename=survey-export-%d-%s.json' % (survey.id, format(datetime.datetime.now(), '%Y%m%d%H%M'))
    return response


def survey_import(request):
    json_blob = request.FILES['data'].read()
    importexport.create_survey_from_json(json_blob)
    return redirect(survey_list)


def chart_data(request, survey_shortname, chart_shortname):
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

def map_tile(request, survey_shortname, chart_shortname, z, x, y):
    if int(z) > 22:
        raise Http404
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

def map_click(request, survey_shortname, chart_shortname, lat, lng):
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

# based on http://djangosnippets.org/snippets/2059/

def urls(request, prefix=''):
    """
        Returns javascript for mapping service endpoint names to urls.

        For this view to work properly, all urls that are to be made
        available and are using regular expressions for defining
        parameters must use named parameters.

        The view uses Django internal url resolver to iterate over a list
        of all currently defined url patterns.  It looks for named patterns
        and replaces each named regex group definition the group name enclosed
        in curley braces.  Url pattern names will be translated into
        javascript variable names by converting all letters to the upper
        case and replacing '-' with '_'.
        """
    resolver = RegexURLResolver(r'^/', settings.ROOT_URLCONF, app_name='pollster', namespace='pollster')

    urls = {}

    for name in resolver.reverse_dict:
        if isinstance(name, str) and name.startswith(prefix):
            url_regex = resolver.reverse_dict.get(name)[1]
            param_names = resolver.reverse_dict.get(name)[0][0][1]
            arg_pattern = r'\(\?P\<[^\)]+\)'  #matches named groups in the form of (?P<name>pattern)

            i = 0
            for match in re.findall(arg_pattern, url_regex):
                url_regex = url_regex.replace(match, "{%s}"%param_names[i])
                i += 1

            urls[name] = "/" + url_regex[:-1]

    return render_with_context(request, "pollster/urls.js", {'urls':urls}, content_type="application/javascript")

def _get_active_survey_user(request):
    gid = request.GET.get('gid', None)
    if gid is None or not request.user.is_active:
        return None
    else:
        return get_object_or_404(SurveyUser, global_id=gid, user=request.user)

def _get_next_url(request, default):
    url = request.GET.get('next', default)
    survey_user = _get_active_survey_user(request)
    if survey_user:
        url = '%s?gid=%s' % (url, survey_user.global_id)
    return url


def specialPrint(msg):
    print >> sys.stderr,msg
