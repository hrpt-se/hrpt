import random

from django.contrib import admin
from django.conf.urls import url
from django.shortcuts import redirect, render
from django.http import HttpResponse

from apps.survey.models import SurveyUser, Profile, Participation, SurveyIdCode


class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'updated', 'valid', 'created')
    ordering = ('user__name',)
    search_fields = ('user__name',)
    list_filter = ('valid',)


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'epidb_id')
    ordering = ('-date',)


class SurveyUserAdmin(admin.ModelAdmin):
    list_display = ('name', 'last_participation_date', 'global_id')
    ordering = ('name',)
    search_fields = ('name',)


class SurveyIdCodeAdmin(admin.ModelAdmin):
    list_display = ('idcode', 'surveyuser_global_id', 'fodelsedatum')
    ordering = ('idcode',)
    search_fields = ('idcode',)

    def save_model(self, request, obj, form, change):
        if obj.surveyuser_global_id == '':
            obj.surveyuser_global_id = None
        if obj.fodelsedatum == '':
            obj.fodelsedatum = None
        obj.save()

    def get_urls(self):
        return [
                   url(r'^delete_unused/$', self.admin_site.admin_view(self.delete_unused), name="remove_unused"),
                   url(r'^generate/$', self.admin_site.admin_view(self.generate_codes), name="generate_codes"),
                ] + super().get_urls()

    def delete_unused(self, request):
        SurveyIdCode.objects.filter(surveyuser_global_id=None).delete()
        self.message_user(request, "All unused SurveyIDCodes have been deleted")
        return redirect(request.META.get('HTTP_REFERER'))

    def generate_codes(self, request):

        def _generate(n=8, retry=0):
            choices = "23456789abcdefghijkmnpqrstuvwxyz"
            c = ''.join(random.SystemRandom().choice(choices) for _ in range(n))
            if SurveyIdCode.objects.filter(idcode=c).exists():
                return _generate(retry=retry + 1)
            SurveyIdCode.objects.create(idcode=c)
            return c

        context = {}
        if request.method == "POST":
            nr_codes = int(request.POST.get("nr_codes", 0))
            codes = [_generate() for _ in range(nr_codes)]

            response = HttpResponse('\n'.join(codes), content_type="text/plain")
            filename = "generated-codes-{}".format(codes[0])
            response['Content-Disposition'] = 'attachment; filename={}.txt'.format(filename)
            return response

        return render(request, "survey_id_code_generate.html", context=context)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Participation, ParticipationAdmin)
admin.site.register(SurveyUser, SurveyUserAdmin)
admin.site.register(SurveyIdCode, SurveyIdCodeAdmin)
