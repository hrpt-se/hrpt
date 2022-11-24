from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def google_analytics():
    try:
        return mark_safe(
            '<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script>'
            '<script>'
            '   window.dataLayer = window.dataLayer || [];'
            '   function gtag(){dataLayer.push(arguments)};'
            '   gtag(\'js\', new Date());'
            '   gtag(\'config\', \'%s\', { \'anonymize_ip\': true });'
            '</script>' % (settings.GA_TRACKING_ID, settings.GA_TRACKING_ID)
        )
    except AttributeError:
        return ''
