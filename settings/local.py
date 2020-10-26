from settings.base import *
from utils import PrivateIPs

DEBUG = True

# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 1025

INTERNAL_IPS = PrivateIPs()

# This setting is populated with empty values unless it already has a value to
# get the dev-environment up and running
try:
    NORECAPTCHA_SITE_KEY
except NameError:
    NORECAPTCHA_SITE_KEY = ''
    NORECAPTCHA_SECRET_KEY = ''
