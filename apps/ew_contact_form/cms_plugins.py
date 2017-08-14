from cms.models import CMSPlugin
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from forms import CaptchaContactForm


class ContactFormPlugin(CMSPluginBase):
    """
    Display a contact form plugin on the page
    """

    model = CMSPlugin
    name = "Contact Form"
    render_template = "contact_form/contact_form_plugin.html"
    cache = False

    def render(self, context, instance, placeholder):
        request = context['request']
        context.update({
            'instance': instance,
            'placeholder': placeholder,
            'form': CaptchaContactForm(request=request),
        })

        return context

plugin_pool.register_plugin(ContactFormPlugin)
