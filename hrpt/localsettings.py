from hrpt.utils import PrivateIPs

### Settings.py för lokal miljö ###

DEBUG = True

ALLOWED_HOSTS = ['*']

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

EPIDB_API_KEY = '0000000000000000000000000000000000000000'
EPIDB_SERVER = 'http://127.0.0.1:8080/'
