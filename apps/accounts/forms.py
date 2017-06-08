from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm

# Needed in pre 1.7 Django to create field specific errors durinng cross field
# checks in clean(). Should be replaced with add_error if upgraded!
from django.forms.utils import ErrorList

from registration.forms import RegistrationForm
from apps.reminder.models import UserReminderInfo
from captcha.fields import CaptchaField

from apps.accounts.models import user_profile
from apps.survey.models import SurveyIdCode

from datetime import datetime

attrs_dict = {'class': 'required'}

class UnicodeRegistrationForm(RegistrationForm):
    username = forms.RegexField(regex=r'(?u)^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(attrs=attrs_dict),
                                label=_("Username"),
                                error_messages={'invalid': _("This value must contain only letters, numbers and underscores.")})

class UnicodeUserChangeForm(UserChangeForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'(?u)^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})

class UnicodeUserCreationForm(UserCreationForm):
    username = forms.RegexField(label=_("Username"), max_length=30, regex=r'(?u)^[\w.@+-]+$',
        help_text = _("Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only."),
        error_messages = {'invalid': _("This value may contain only letters, numbers and @/./+/-/_ characters.")})


class EmailSettingsForm(forms.Form):
    email = forms.EmailField(label=_("Email"))
    #send_reminders = forms.BooleanField(label=_("Send reminders"), help_text=_("Check this box if you wish to receive weekly reminders throughout the flu season"), required=False)
    #language = forms.ChoiceField(label=_("Language"), choices=settings.LANGUAGES)

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance')
        self.reminder_info, _ = UserReminderInfo.objects.get_or_create(user=self.instance, defaults={'active': True, 'last_reminder': self.instance.date_joined})

        initial = kwargs.pop('initial', {})
        initial['email'] = self.instance.email
        initial['send_reminders'] = self.reminder_info.active
        initial['language'] = self.reminder_info.language if self.reminder_info.language else settings.LANGUAGE_CODE
        kwargs['initial'] = initial

        super(EmailSettingsForm, self).__init__(*args, **kwargs)

        if len(settings.LANGUAGES) == 1:
            del self.fields['language']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.exclude(id=self.instance.id).filter(email=email).count():
            raise forms.ValidationError(_("This email is already in use"))
        return email

    def save(self):
        if self.instance.email == self.instance.username:
            self.instance.username = self.cleaned_data['email']
        self.instance.email = self.cleaned_data['email']

        # Reminders are not used anymore.
        # self.reminder_info.active = self.cleaned_data['send_reminders']

        if 'language' in self.cleaned_data:
            self.reminder_info.language = self.cleaned_data['language']

        self.instance.save()
        self.reminder_info.save()


class UsernameForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', )

    def clean_username(self):
        value = self.cleaned_data['username']

        if User.objects.exclude(pk=self.instance.pk).filter(username=value).count():
            raise forms.ValidationError(_("A user with this username already exists"))

        return value


class DeactivationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('is_active', )

    def clean_is_active(self):
        value = self.cleaned_data['is_active']

        return value


class CaptchaUnicodeRegistrationForm(RegistrationForm):
    username = forms.RegexField(
        regex=r'(?u)^[\w.@+-]+$',
        max_length=30,
        widget=forms.TextInput(attrs=attrs_dict),
        label=_("Username"),
        help_text=_("Choose a name you want to use for login. "
                    "For example: anders2009"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores.")
        }
    )

    # Override the email-field from the super-class to add a field label
    email = forms.EmailField(
        label=_(u'Email address'),
        required=True
    )

    password1 = forms.CharField(
        min_length=5,
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password"),
        help_text=_("At least 5 characters")
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs=attrs_dict, render_value=False),
        label=_("Password (again)"),
        help_text=_("Repeat the same password")
    )

    idcode = forms.CharField(
        max_length=10,
        label=_("Activation code"),
        help_text=_("Please enter the code from your invitation letter here.")
    )

    max_birthyear = datetime.today().year
    min_birthyear = max_birthyear - 86 # Should be max 85 years old, but if born 31 december it could be 86 years ago

    yearofbirth = forms.IntegerField(
        max_value=max_birthyear,
        min_value=min_birthyear,
        label=_("Year of birth"),
        help_text=_("Please enter the 4 digits of your year of birth. "
                    "For example: 1989"),
        error_messages={'invalid': _("This value must contain 4 digits.")
        }
    )

    captcha = CaptchaField(
        label=_("Captcha"),
        help_text=_("Please enter the characters shown in the image.")
    )

    def clean(self):
        super(CaptchaUnicodeRegistrationForm, self).clean() #Perform cleaning of the orginal form first!

        data = self.cleaned_data.get('idcode')
        captcha = self.cleaned_data.get('captcha')

        #Only check if captcha correct
        if captcha and data:
            #Check if idcode actually exist in our table
            not_exist = False
            in_use = False

            try:
                SurveyIdcode_id = SurveyIdCode.objects.get(idcode=data)
            except:
                not_exist = True

            #Check if the code has alreay been used to register a user
            #This is a bit tricky as the tegistration only is done after using the confirmation link
            #that the user can only click after this step. So there is a possibility that two persons
            #register with the same idcode anyhow.
            try:
                SurveyIdcode_id = SurveyIdCode.objects.get(idcode=data)
                if SurveyIdcode_id.surveyuser_global_id:
                    in_use = True
            except:
                not_exist = True

            # Needed in pre 1.7 Django to create field specific errors durinng cross field
            # checks in clean(). Should be replaced with add_error if upgraded!

            if not_exist:
                errors = self._errors.setdefault("idcode", ErrorList())
                errors.append(_("Check the code in you letter. This code is incorrect."))
            if in_use:
                errors = self._errors.setdefault("idcode", ErrorList())
                errors.append(_("This code has already been used. Is the code correct? Or did you already register?"))
            # if not_exist:
            #     self.add_error("idcode", "Check the code in you letter. This code is incorrect")
            # if in_use:
            #     self.add_error("idcode", "This code has already been used. Is the code correct? Or did you already register?")
        return self.cleaned_data



class CaptchaPasswordResetForm(PasswordResetForm):
    captcha = CaptchaField(label=_("Captcha"),
                           help_text=_("Please enter the characters shown in the image."))
