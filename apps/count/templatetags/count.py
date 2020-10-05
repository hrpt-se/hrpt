from __future__ import absolute_import

from urllib import request

from django.template import Library, Node
from django.contrib.sites.models import Site
from django.core.cache import cache 
from django.conf import settings

register = Library()

SOURCES = {
    'nl': 'http://www.degrotegriepmeting.nl/count/counter/?country=NL',
    'be': 'http://www.degrotegriepmeting.nl/count/counter/?country=BE',
    'de': 'http://www.aktivgegengrippe.de/count/counter/',
    'at': 'http://www.aktivgegengrippe.at/count/counter/',
    'ch': 'http://www.aktivgegengrippe.ch/count/counter/',
    'se': 'https://www.halsorapport.se/count/counter/',
    'uk': 'http://flusurvey.org.uk/count/counter/',
    'it': 'http://www.influweb.it/count/counter/',
    'pt': 'http://www.gripenet.pt/count/counter/',
    'fr': 'http://www.grippenet.fr/count/counter/',
}

def do_member_count(parser, token):
    contents = token.split_contents()
    assert len(contents) == 2, "%r tag requires a single argument" % contents[0]
    country = contents[1]
    assert country[0] in ['"', "'"], "argument must be a string"
    country = country[1:-1]
    return MemberCountNode(country)

class MemberCountNode(Node):
    def __init__(self, country):
        self.country = country 

    @classmethod
    def get(cls, country):
        key = "count-counter-%s" % country
        if cache.get(key):
            return cache.get(key)

        try:
            result = request.urlopen(SOURCES[country], timeout=0.1 if settings.DEBUG else 0.08).read()
        except:
            result = '2300'

        try:
            int(result)
        except ValueError:
            result = '0'

        cache.set(key, result, timeout=0 * 30) # timeout 30 minutes
        return result 

    def render(self, context):
        if self.country == 'total':
            return "%s" % sum([int(self.get(country)) for country in SOURCES.keys()])

        return self.get(self.country)


register.tag('member_count', do_member_count)
