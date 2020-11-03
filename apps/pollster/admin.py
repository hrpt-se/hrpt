from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, CHANGE
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

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
            survey_user.name = username
            survey_user.save()

    batch_obfuscate.short_description = 'Obfuscate selected users'


admin.site.unregister(User)
admin.site.register(User, ExtendedUserAdmin)
admin.site.register(Survey, SurveyAdmin)
