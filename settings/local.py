from base import *
from utils import PrivateIPs

DEBUG = True

# MIDDLEWARE += (
#     'debug_toolbar.middleware.DebugToolbarMiddleware',
# )

# INSTALLED_APPS += (
#     'debug_toolbar',
# )

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = PrivateIPs()
