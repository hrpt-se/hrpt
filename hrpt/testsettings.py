from hrpt.deployed import *

### Settings.py för testmiljön ###

ADMINS = (
    ('hrpt admin', 'admin@mail'),
)

MANAGERS = ADMINS

EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_PORT = 25

# https://docs.djangoproject.com/en/2.2/ref/settings/#allowed-hosts
# Punkt i början betyder valfri subdomän t.ex. "www"
ALLOWED_HOSTS = secrets.ALLOWED_HOSTS

# Debug ska generellt vara avstängt av säkerhetsskäl men kan sättas på temporärt under aktiv testning:
Debug = False
