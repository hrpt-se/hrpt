from django.contrib import admin, messages
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import render
from django.http import HttpResponseRedirect

from .models import RuleType, QuestionDataType, VirtualOptionType, Survey, TranslationSurvey, Chart

admin.site.register(RuleType)
admin.site.register(QuestionDataType)
admin.site.register(VirtualOptionType)
admin.site.register(TranslationSurvey)
admin.site.register(Chart)


class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title',)
    readonly_fields = ('status',)


current_user_admin = type(admin.site._registry[User])


class ExtendedUserAdmin(current_user_admin):
    actions = [
        'batch_deactivate',
        'batch_obfuscate',
        'remove_response',
    ]

    def batch_deactivate(self, request, queryset):

        ct = ContentType.objects.get_for_model(queryset.model)
        for obj in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ct.pk,
                object_id=obj.pk,
                object_repr=obj.username,
                action_flag=CHANGE,
                change_message='User deactivated as part of a batch operation.')

            obj.is_active = False
            obj.save()

        pass

    batch_deactivate.short_description = 'Deactivate selected users'

    def batch_obfuscate(self, request, queryset):
        # Exclude all users that are already obfuscated (correctly) or are still active
        total = queryset.count()
        queryset = queryset.exclude(is_active=True).exclude(
            Q(username__startswith="AVAKT_USER") & Q(surveyuser__name__startswith="AVAKT_USER"))
        content_type = ContentType.objects.get_for_model(queryset.model)

        for user in queryset:
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=content_type.pk,
                object_id=user.pk,
                object_repr=user.username,
                action_flag=CHANGE,
                change_message='User email and username obfuscated as part of batch operation.'
            )
            username = "AVAKT_USER{}".format(user.pk)
            user.email = "{}@nowhere.spc".format(username)
            user.username = username
            user.save()

            survey_user = user.surveyuser_set.first()
            if survey_user:
                survey_user.name = username
                survey_user.save()

        self.message_user(request, "Obfuscated {} out of {} selected users".format(queryset.count(), total))

    batch_obfuscate.short_description = 'Obfuscate selected users'

    def _get_surveys(self, users):
        surveys = Survey.objects.filter(status="PUBLISHED")
        return [s for s in surveys if s.as_model().objects.filter(user__in=users).exists()]

    def _remove_responses(self, request, users):
        survey = Survey.objects.get(shortname=request.POST.get("survey"), status="PUBLISHED")
        responses = survey.as_model().objects.filter(user__in=users)
        count = responses.count()
        responses.delete()
        return count, survey.shortname

    def remove_response(self, request, queryset):
        # If the form is being submitted, remove responses to the selected survey
        # and display the results.
        if request.POST.get("do_action", False):
            result = self._remove_responses(request, queryset)
            self.message_user(request, "Removed {} response(s) to survey {}".format(*result))
            return HttpResponseRedirect(request.get_full_path())

        # Get all surveys that any of the selected users have answered.
        # If no answers were found, warn and return.
        surveys = self._get_surveys(queryset)
        if not surveys:
            self.message_user(request, "Selected users have not answered any surveys", messages.WARNING)
            return HttpResponseRedirect(request.get_full_path())
        return render(
            request,
            "remove_response.html",
            context={
                "users": queryset,
                "surveys": surveys,
            }
        )

    remove_response.short_description = "Remove response to a survey"


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Survey, SurveyAdmin)
