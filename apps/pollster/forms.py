from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.models import User
from django.conf import settings
from apps.pollster.models import SurveyGroup
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


class SurveyAccessOptionsForm(forms.ModelForm):
    class Meta:
        model = SurveyGroup
        fields = ["all_active"]
        help_texts = {
            "all_active": """Enabling this option will allow all active users to access the survey. 
            This option will override any filter or user selections.""",
        }


class SurveyAccessFiltersForm(forms.ModelForm):
    from_year = forms.IntegerField(
        required=False, min_value=1900, max_value=2040, help_text="", label="From birthyear")
    to_year = forms.IntegerField(
        required=False, min_value=1900, max_value=2040,
        help_text="Enter a year from 1900-2040 or leave blank", label="To birthyear")

    from_joined = forms.DateField(
        required=False, widget=forms.widgets.DateInput(format='%Y-%m-%d', attrs={"type": "date"}))
    to_joined = forms.DateField(
        required=False, widget=forms.widgets.DateInput(format='%Y-%m-%d', attrs={"type": "date"}),
        help_text="Select a to/from date to filter users based on the date of registration")

    class Meta:
        model = SurveyGroup
        fields = ["from_year", "to_year", "from_joined", "to_joined"]


class SurveyAccessUsersForm(forms.ModelForm):
    user_file = forms.FileField(
        required=False, label="Upload users",
        help_text="""Select a .csv or .txt file containing a column of User IDs. 
        The users in your file will be added when the form is saved.
        IDs that do not match any active user will be ignored.""")

    class Meta:
        model = SurveyGroup
        fields = ["users"]
        widgets = {
            "users": FilteredSelectMultiple("Users", is_stacked=False),
        }

    class Media:
        css = {'all': ('/static/admin/css/widgets.css',), }
        js = ('/admin/jsi18n/',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["users"].required = False
        self.fields["users"].queryset = User.objects.filter(is_active=True) | self.instance.users.filter(is_active=False)
