from os import environ

from base import *

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.fohmdev.local'
