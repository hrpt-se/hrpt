# This file contains shared settings for deployed environments,
# i.e. stage and prod. It should not be referenced directly.

from hrpt.base import *

# DEBUG = False

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

NORECAPTCHA_SITE_KEY = secrets.NORECAPTCHA_SITE_KEY
NORECAPTCHA_SECRET_KEY = secrets.NORECAPTCHA_SECRET_KEY
