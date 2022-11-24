from datetime import datetime

from django import forms
from django.utils.translation import ugettext_lazy as _
from djangocms_text_ckeditor.widgets import TextEditorWidget
from parler.forms import TranslatableModelForm

from .models import (
    NO_INTERVAL, ReminderSettings, NewsLetterTemplate, NewsLetter,
    get_default_for_newsitem, get_upcoming_dates, get_settings
)


class ReminderSettingsForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super(ReminderSettingsForm, self).clean()
        if cleaned_data.get('send_reminders'):
            if (cleaned_data.get('interval') != NO_INTERVAL
                    and not (cleaned_data.get('begin_date')
                             and cleaned_data.get('interval'))):
                raise forms.ValidationError(
                    _("If 'send_reminders' is checked the other fields "
                      "pertaining to reminders are required")
                )
        return cleaned_data

    class Meta:
        model = ReminderSettings
        fields = '__all__'


class NewsLetterTemplateForm(TranslatableModelForm):
    message = forms.CharField(widget=TextEditorWidget())

    class Meta:
        model = NewsLetterTemplate
        fields = (
            'is_default_reminder',
            'is_default_newsitem',
            'sender_email',
            'sender_name',
            'subject',
            'message'
        )


class NewsLetterForm(TranslatableModelForm):
    message = forms.CharField(widget=TextEditorWidget())
    date = forms.ChoiceField(
        help_text=_("If no dates are shown here, check your site settings")
    )

    def __init__(self, *args, **kwargs):
        super(NewsLetterForm, self).__init__(*args, **kwargs)
        
        if get_settings() and get_settings().interval == NO_INTERVAL: 
            self.fields['date'] = forms.DateField()
        else:
            self.fields['date'].choices = get_upcoming_dates(datetime.now())

        # I don't understand where self.language comes from, it must be some
        # magic in TranslatableModelForm but I can't identify it; in any case
        # we need some default for tests
        if not hasattr(self, 'language'):
            self.language = 'en'

        for fieldname in ('sender_email', 'sender_name', 'subject', 'message'):
            default = get_default_for_newsitem(self.language)
            self.fields[fieldname].initial = getattr(default, fieldname, "")

    class Meta:
        model = NewsLetter
        fields = '__all__'
