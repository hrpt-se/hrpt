from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext_lazy as _

from .models import SurveyListPlugin, SurveyUser
from apps.pollster.models import Survey as pollster_survey_model

# Oh well, this doesn't really belong in the survey apps, should probably be in
# the pollster app instead


class ListUserSurveysPlugin(CMSPluginBase):
    model = SurveyListPlugin
    render_template = "cms_plugin_survey_list.html"
    name = "User Survey List"
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']

        try:
            global_id = request.user.surveyuser_set.first().global_id
        except AttributeError:
            global_id = None

        #no idea why this is being evaluated on every page view
        # but oh well.. make it return the original contect anyway
        # we only need this in pages with the guid anyway
        if not global_id:
            return context

        open_surveys = []
        replied_surveys = []

        # this is so we make sure that the global_id belongs to the authenticated user
        survey_user = SurveyUser.objects.get(global_id=global_id, user=request.user)
        if survey_user:
            replied_surveys, open_surveys, locked_surveys, locked_terms_surveys = pollster_survey_model.\
                get_user_open_surveys(global_id, request.user)

        import sys
        #print >> sys.stderr,profile
        #print >> sys.stderr, request.user.id

        context.update({
            'global_id': global_id, # I think this is already in request.user. #TODO: clean up
            'user_id': request.user.id,
            'object': instance,
            'placeholder': placeholder,
            'open_surveys': open_surveys,
            'replied_surveys': replied_surveys,
            'locked_surveys' : locked_surveys,
            'locked_terms_surveys' : locked_terms_surveys
        })
        return context

plugin_pool.register_plugin(ListUserSurveysPlugin)
