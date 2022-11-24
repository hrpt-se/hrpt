from django.contrib import admin
from django.contrib.auth.models import User
from django import forms

from apps.accounts.forms import UnicodeUserChangeForm, UnicodeUserCreationForm
from .models import UserProfile
from apps.survey.models import SurveyUser

current_user_admin = type(admin.site._registry[User])


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    extra = 0  # only show UserProfiles that exist


class SurveyIDCodeForm(forms.ModelForm):
    # Form that uses SurveyUser to add `fodelsedatum` to the user admin view.
    # This is because the SurveyIDCode does not have a direct foreign key
    # relation with auth.User.
    year = forms.IntegerField(min_value=1900, initial=1950)

    def __init__(self, *args, **kwargs):
        # Initialize the year to SurveyIDCode.fodelsedatum
        user = kwargs.get("instance")
        if user:
            year = user.surveyidcode_set.first().fodelsedatum
            if year and year.isdecimal():
                self.base_fields["year"].initial = int(year)

        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        # Override the save and only save the year of birth to the SurveyIDCode
        year = self.cleaned_data.get("year", None)
        user = self.cleaned_data.get("id", None)
        if year and user:
            id_code = user.surveyidcode_set.first()
            id_code.fodelsedatum = str(year)
            id_code.save()

    class Meta:
        fields = ["year"]


class SurveyIDCodeInline(admin.StackedInline):
    model = SurveyUser
    form = SurveyIDCodeForm
    extra = 0

    verbose_name = "Year of birth"
    verbose_name_plural = "Year of birth"

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class UnicodeUserAdmin(current_user_admin):
    form = UnicodeUserChangeForm
    add_form = UnicodeUserCreationForm
    inlines = [SurveyIDCodeInline, UserProfileInline]


admin.site.unregister(User)
admin.site.register(User, UnicodeUserAdmin)
