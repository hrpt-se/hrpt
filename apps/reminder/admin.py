from django.contrib.auth.models import User
from django.contrib import admin, messages
from django.contrib.sites.models import Site
from django.http import HttpResponseRedirect
from django.db.models import Count, F

from parler.admin import TranslatableAdmin

from .models import (
    UserReminderInfo, ReminderSettings, NewsLetterTemplate, NewsLetter,
    ReminderError, ManualNewsLetter
)
from .forms import ReminderSettingsForm, NewsLetterTemplateForm, NewsLetterForm


@admin.register(UserReminderInfo)
class UserReminderInfoAdmin(admin.ModelAdmin):
    list_display = ('user', 'active', 'last_reminder')
    ordering = ('user__username',)
    actions = ('make_active', 'make_inactive')
    list_editable = ('active',)
    list_filter = ('active',)
    search_fields = ('user__username',)

    def get_actions(self, request):
        actions = super(UserReminderInfoAdmin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def make_active(self, request, queryset):
        queryset.update(active=True)

    make_active.short_description = 'Make selected reminders active'

    def make_inactive(self, request, queryset):
        queryset.update(active=False)

    make_inactive.short_description = 'Make selected reminders inactive'

class UserReminderInfoInline(admin.StackedInline):
    model = UserReminderInfo


current_user_admin = type(admin.site._registry[User])


class InfoUserAdmin(current_user_admin):
    inlines = current_user_admin.inlines + [UserReminderInfoInline]

admin.site.unregister(User)
admin.site.register(User, InfoUserAdmin)


class SiteSettingsInline(admin.StackedInline):
    model = ReminderSettings
    form = ReminderSettingsForm

current_site_admin = type(admin.site._registry[Site])


class ReminderSiteAdmin(current_site_admin):
    inlines = current_site_admin.inlines + [SiteSettingsInline]

admin.site.unregister(Site)
admin.site.register(Site, ReminderSiteAdmin)


@admin.register(NewsLetterTemplate)
class NewsLetterTemplateAdmin(TranslatableAdmin):
    form = NewsLetterTemplateForm
    actions = ('manual_send_newsletter', )

    def manual_send_newsletter(self, request, queryset):
        if queryset.count() > 1:
            self.message_user(
                request,
                "Can only manually send one template at a time",
                level=messages.ERROR
            )

            return

        template = queryset.first()

        return HttpResponseRedirect(
            '/admin/manual-newsletters/templates/%s' % template.id)


@admin.register(NewsLetter)
class NewsLetterAdmin(TranslatableAdmin):
    form = NewsLetterForm
    list_display = ("__unicode__", "date")


@admin.register(ReminderError)
class ReminderErrorAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "message", "user", "email")
    search_fields = ('user__username', 'user__email',)


class EmailQueue(ManualNewsLetter):
    class Meta:
        proxy = True
        verbose_name = "Email queue"
        verbose_name_plural = "Email queue"


@admin.register(EmailQueue)
class EmailQueueAdmin(admin.ModelAdmin):
    change_list_template = "email_queue_change_list.html"
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        extra_context = {"title": "Email Queue"}
        response = super().changelist_view(request, extra_context=extra_context)

        try:
            qs = response.context_data["cl"].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            "queued": Count("queuedemail", distinct=True),
            "sent": Count("sentemail", distinct=True),
            "failed": Count("failedemail", distinct=True),
        }

        response.context_data["summary"] = qs.annotate(**metrics).annotate(
            total=F("queued") + F("sent") + F("failed")
        ).order_by("-timestamp")

        return response
