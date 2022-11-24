# this is used to run the website with apache and mod_wsgi

import os

from django.core.wsgi import get_wsgi_application

os.chdir(os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hrpt.settings')

application = get_wsgi_application()
