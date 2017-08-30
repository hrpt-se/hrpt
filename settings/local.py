from base import *
from utils import PrivateIPs

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = PrivateIPs()
