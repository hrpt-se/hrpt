from django import forms
from django.utils.translation import ugettext_lazy as _

from django.conf import settings
from .models import Chart


class SurveyXmlForm(forms.Form):
    surveyxml = forms.CharField(required=True)


class SurveyTranslationAddForm(forms.Form):
    language = forms.ChoiceField(label="Language", required=True, choices=settings.LANGUAGES)


class SurveyChartAddForm(forms.Form):
    shortname = forms.RegexField(label="Short Name", max_length=30, regex=r'^[a-zA-Z0-9_]+$', required=True)


class SurveyChartEditForm(forms.ModelForm):
    shortname = forms.RegexField(label="Short Name", max_length=30, regex=r'^[a-zA-Z0-9_]+$', required=True,
                                 error_messages={
                                     'invalid': _('Enter a valid value consisting of letters, numbers or underscores')})
    chartwrapper = forms.CharField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Chart
        fields = ('type', 'shortname', 'chartwrapper', 'sqlsource', 'sqlfilter', 'status')


class SurveyImportForm(forms.Form):
    data = forms.FileField(label="Survey definition", required=True)


class SurveyExtendedResultsForm(forms.Form):
    email = forms.BooleanField(required=False, initial=True, label=_('Email address'))
    is_active = forms.BooleanField(required=False, initial=True, label=_('User is active'))
    id_code = forms.BooleanField(required=False, initial=True, label=_('ID code'))
    dob_from_idcode = forms.BooleanField(required=False, initial=False, label=_('Date of Birth from id_code-table'))
