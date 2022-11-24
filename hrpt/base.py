# Django settings for epiweb project.
# -*- coding: utf-8 -*-

# base.py ska vara gemensam för alla tänkbara miljöer (t.ex. local, dev, test, stage, prod), unika inställningar läggs i separata filer

import os

from django.utils.log import DEFAULT_LOGGING
from _secrets import secrets

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH = PROJECT_ROOT

MEDIA_ROOT = os.path.join(BASE_DIR, 'upload/')

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'media/')
]

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

POLLSTER_CACHE_PATH = PROJECT_PATH

SECRET_KEY = secrets.DJANGO_SECRET

# Enable draft save
DRAFT_SAVE = True

# Enable the group functionality
SURVEY_GROUPS = True

ADMINS = (
    ('hrpt Admin', 'admin@email'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql',
        'NAME': secrets.DB_NAME,
        'HOST': secrets.DB_HOST,
        'USER': secrets.DB_USERNAME,
        'PASSWORD': secrets.DB_PASSWORD,
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Add handler for logging to files
LOGGING = DEFAULT_LOGGING
LOGGING["formatters"]["file"] = {
    'format': '[%(asctime)s] %(message)s',
}
# Loggningsnivå ERROR:
LOGGING["handlers"]["file"] = {
    'level': 'ERROR',
    'formatter': "file",
    'filters': ['require_debug_false'],
    'class': 'logging.handlers.TimedRotatingFileHandler',
    'filename': "/opt/hrpt/log/hrpt/halsorapport.log",
    'when': 'midnight',
    'backupCount': 0,  # 0 keeps all logs, change to the desired nr to save
}
# Loggningsnivå DEBUG:
# LOGGING["handlers"]["file"] = {
#     'level': 'DEBUG',
#     'formatter': "file",
#     'class': 'logging.handlers.TimedRotatingFileHandler',
#     'filename': "/opt/hrpt/log/hrpt/halsorapport_debug.log",
#     'when': 'midnight',
#     'backupCount': 0,  # 0 keeps all logs, change to the desired nr to save
# }

LOGGING["loggers"]["django"]["handlers"] += ["file"]

CMS_PERMISSION = True

SITE_ID = 1

# https://docs.djangoproject.com/en/2.2/ref/settings/#password-hashers
# Om gamla SHA1 ska bytas ut måste lösenord i DB hashas om, leta upp guide i så fall
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher'
]

# https://docs.djangoproject.com/en/2.2/ref/settings/#time-zone-1
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sv'
FORMAT_MODULE_PATH = 'formats'

# Tillagd efter klagomål från Django:
LANGUAGE_COOKIE_HTTPONLY = False
LANGUAGE_COOKIE_SAMESITE = False
LANGUAGE_COOKIE_SECURE = False

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

# For checking postcodes etc.
# Use ISO3166 two-letter country code
# See http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
# Available: be, it, nl, uk, pt, se
COUNTRY = 'se'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

LANGUAGES = (
    ('en', 'English'),
    ('de', 'Deutsch'),
    ('fr', 'Français'),
    ('nl', 'Nederlands'),
    ('it', 'Italiano'),
    ('sv', 'Svenska'),
    ('pt', 'Português'),
    ('es', 'Español')
)

CMS_LANGUAGES = {
    'default': {
        'public': True,
        'hide_untranslated': False,
        'redirect_on_fallback': True,
    },
    1: [
        {
            'public': True,
            'code': 'sv',
            'hide_untranslated': False,
            'name': 'sv',
            'redirect_on_fallback': True,
        }
    ],
}

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/static/'
# OBS, även om nya standarden är /media/ så ska vi behålla /upload/ för att länkarna ska bli rätt i sökmotorer som indexerat gamla hemsidan
MEDIA_URL = '/upload/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Mappen existerar varken lokalt eller i testmiljö, oklart om det är gammal rest eller något som automatgenereras.
CMS_FILE_ICON_PATH = os.path.join(MEDIA_ROOT, 'file_icons/')
CMS_FILE_ICON_URL = os.path.join(MEDIA_URL, 'file_icons/')
FILER_IMAGE_USE_ICON = True

MIDDLEWARE = (
    'cms.middleware.utils.ApphookReloadMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'cms.middleware.page.CurrentPageMiddleware',
    'cms.middleware.user.CurrentUserMiddleware',
    'cms.middleware.toolbar.ToolbarMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'cms.middleware.language.LanguageCookieMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware'
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [os.path.join(BASE_DIR, 'templates')],
    'OPTIONS': {
        'context_processors': (
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.i18n",
            "django.template.context_processors.request",
            "django.template.context_processors.media",
            'django.template.context_processors.csrf',
            "django.template.context_processors.debug",
            "sekizai.context_processors.sekizai",
            "django.contrib.messages.context_processors.messages",
            "apps.partnersites.context_processors.customizations",
            "django.template.context_processors.static",
            'cms.context_processors.cms_settings'
        ),
        'loaders': [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ],
    }
}]

CMS_TEMPLATES = (
    ('hrpt-responsive/twocol.html', '2 Columns'),
    ('hrpt-responsive/singlecol.html', 'Single Column'),
    ('hrpt-responsive/twocol_submenu.html', '2 Columns with submenu')
)

GEOMETRY_TABLES = (
    ('pollster_zip_codes', 'zip level'),
)

ROOT_URLCONF = 'hrpt.urls'

WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.humanize',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'parler',
    'sekizai',
    'django_registration',
    'loginurl',
    'apps.accounts',
    'apps.survey',
    'apps.reminder',
    'contact_form',
    'apps.hrptinfo',
    'apps.partnersites',
    'apps.count',
    'cms',
    'treebeard',
    'menus',
    'apps.pollster',
    'nocaptcha_recaptcha',
    'pytils',
    'sorl.thumbnail',
    'pure_pagination',
    'djangocms_text_ckeditor',
    'djangocms_link',
    'djangocms_file',
    'djangocms_admin_style',
    'filer',  # Required for djangocms_picture
    'easy_thumbnails',  # Required for djangocms_picture
    'djangocms_picture'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'loginurl.backends.LoginUrlBackend'
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

CMSPLUGIN_NEWS_RSS_TITLE = "News"
CMSPLUGIN_NEWS_RSS_DESCRIPTION = "News List"

CMS_MEDIA_URL = '/static/cms/'

THUMBNAIL_PROCESSORS = (
    'easy_thumbnails.processors.colorspace',
    'easy_thumbnails.processors.autocrop',
    'filer.thumbnail_processors.scale_and_crop_with_subject_location',
    'easy_thumbnails.processors.filters'
)

ACCOUNT_ACTIVATION_DAYS = 7

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'Hälsorapport <halsorapport@folkhalsomyndigheten.se>'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Influenzanet] '

SURVEY_ID = 'gold-standard-weekly-1.6'
SURVEY_PROFILE_ID = 'gold-standard-intake-1.5'

MOBILE_INTERFACE_ACTIVE = False

STORE_RESPONSES_LOCALLY = False

# SEO Settings

GOOGLE_ANALYTICS_ACCOUNT = None
CMS_SEO_FIELDS = True

SESSION_COOKIE_AGE = 60 * 60 * 2

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

LOGIN_REDIRECT_URL = '/sv/valkommen/'
URL_SCHEME = 'http'

MULTI_PROFILE_ALLOWED = 'false'  # pekka

# Allow iframes in the ckeditor
TEXT_ADDITIONAL_TAGS = ('iframe',)
TEXT_ADDITIONAL_ATTRIBUTES = ('allow', 'allowfullscreen', 'frameborder')
