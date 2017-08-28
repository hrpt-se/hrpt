# This file contains shared settings for deployed environments,
# i.e. stage and prod. It should not be referenced directly.

from base import *

DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
