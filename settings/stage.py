from base import *

DEBUG = False

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.SHA1PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher'
]

ALLOWED_HOSTS = '*'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.fohmdev.local'
