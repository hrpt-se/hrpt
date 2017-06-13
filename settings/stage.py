from os import environ

from base import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'halsorapportdev-srv3',
        'HOST': 'mariadb-srv.fohmdev.local',
        'USER': 'halsorap-srv3',
        'PASSWORD': environ['DB_PASSWORD']
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.fohmdev.local'
