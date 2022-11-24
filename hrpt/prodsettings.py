from hrpt.deployed import *

### settings.py för prodmiljön ###

DEBUG = False

ADMINS = (
    ('hrpt Admin', 'admin@email'),
)

MANAGERS = ADMINS

EMAIL_HOST = secrets.EMAIL_HOST
# EMAIL_PORT = 25
URL_SCHEME = 'https'

# Enable draft save
DRAFT_SAVE = True

# Enable the group functionality
SURVEY_GROUPS = True

ALLOWED_HOSTS = secrets.ALLOWED_HOSTS
