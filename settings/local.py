from base import *
from utils import PrivateIPs

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'epiwork',
        'HOST': 'localhost',
        'USER': 'epiwork',
        'PASSWORD': 'epiwork'
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

INTERNAL_IPS = PrivateIPs()