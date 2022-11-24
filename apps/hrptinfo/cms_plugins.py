from django.utils.translation import ugettext as _

from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import NewsItem
from .forms import CaptchaContactForm


class ContactFormPlugin(CMSPluginBase):
    """
    Display a contact form plugin on the page
    """

    model = CMSPlugin
    name = "Contact Form"
    render_template = "contact_form_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'form': CaptchaContactForm(request=request),
        })

        return context


class NewsList(CMSPluginBase):
    render_template = 'news_list.html'
    name = _('News List')
    allow_children = True
    child_classes = ('NewsItemPublisher', )
    cache = False


class NewsItemPublisher(CMSPluginBase):
    model = NewsItem
    name = _('News item')
    render_template = 'news_item.html'
    cache = False


plugin_pool.register_plugin(ContactFormPlugin)
plugin_pool.register_plugin(NewsList)
plugin_pool.register_plugin(NewsItemPublisher)