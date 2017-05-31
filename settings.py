# Django settings for epiweb project.
# -*- coding: utf-8 -*-

import os
from utils import PrivateIPs

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'epiwork',
        'HOST': 'localhost',
        'USER': 'epiwork',
        'PASSWORD': 'epiwork'
    }
}

ADMINS = (
    ('halsorapport Admin', 'admin.halsorapport@folkhalsomyndigheten.se'),
)

MANAGERS = ADMINS


SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'sv'
# LANGUAGE_CODE = 'en'
FORMAT_MODULE_PATH = 'formats'

# For checking postcodes etc.
# Use ISO3166 two-letter country code
# See http://www.iso.org/iso/country_codes/iso_3166_code_lists/english_country_names_and_code_elements.htm
# Avaliable: be, it, nl, uk, pt, se
COUNTRY = 'se'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

LANGUAGES = (
   ('en', u'English'),
   ('de', u'Deutsch'),
   ('fr', u'Français'),
   ('nl', u'Nederlands'),
   ('it', u'Italiano'),
   ('sv', u'Svenska'),
   ('pt', u'Português'),
   ('es', u'Español'),
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

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
import os
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')
LOCALE_PATHS = (
    os.path.join(PROJECT_PATH, 'locale'),
)
POLLSTER_CACHE_PATH = PROJECT_PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
STATIC_URL = '/static/'
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

CMS_FILE_ICON_PATH = os.path.join(MEDIA_ROOT, 'file_icons/')
CMS_FILE_ICON_URL = os.path.join(MEDIA_URL, 'file_icons/')

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'swgm*3%po62mg76m4iq!k8h3j+_)x=8b--7skjc_0wiak^wksr'


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
    'cms.middleware.language.LanguageCookieMiddleware'
)


TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['templates'],

    'OPTIONS': {
        'context_processors': (
            "django.contrib.auth.context_processors.auth",
            "django.template.context_processors.i18n",
            "django.template.context_processors.request",
            "django.template.context_processors.media",
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
            'django.template.loaders.eggs.Loader'
        ],
    }
}]


CMS_TEMPLATES = (
    ('base/threecol.html', "3 Columns"),
    ('base/twocol.html', "2 Columns"),
    ('base/influhome.html', "European Map"),
    ('base/sitebase.html', "Base")
)

GEOMETRY_TABLES = (
 ('pollster_zip_codes','zip level'),
)

ROOT_URLCONF = 'urls'


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'hvad',
    'sekizai',
    'registration',
    'loginurl',
    'apps.accounts',
    'apps.survey',
    'apps.reminder',
    'apps.journal',
    'contact_form',
    'apps.ew_contact_form',
    'apps.partnersites',
    'apps.count',
    'cms',
    'treebeard',
    'menus',
    'apps.pollster',
    'captcha',
    'pytils',
    'sorl.thumbnail',
    'pure_pagination',
    'djangocms_text_ckeditor',
    'djangocms_link',
    'djangocms_admin_style'
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'loginurl.backends.LoginUrlBackend',
)

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

CMSPLUGIN_NEWS_RSS_TITLE = "News"
CMSPLUGIN_NEWS_RSS_DESCRIPTION = "News List"

CMS_MEDIA_URL = '/media/cms/'

ACCOUNT_ACTIVATION_DAYS = 7

# Default e-mail address to use for various automated correspondence from
# the site managers.
DEFAULT_FROM_EMAIL = 'Hälsorapport <halsorapport@folkhalsomyndigheten.se>'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Subject-line prefix for email messages send with django.core.mail.mail_admins
# or ...mail_managers.  Make sure to include the trailing space.
EMAIL_SUBJECT_PREFIX = '[Influenzanet] '

EPIDB_API_KEY = '0000000000000000000000000000000000000000'
EPIDB_SERVER = 'http://127.0.0.1:8080/'

SURVEY_ID = 'gold-standard-weekly-1.6'
SURVEY_PROFILE_ID = 'gold-standard-intake-1.5'

MOBILE_INTERFACE_ACTIVE = False

STORE_RESPONSES_LOCALLY = False

# SEO Settings

GOOGLE_ANALYTICS_ACCOUNT = None
CMS_SEO_FIELDS = True

SESSION_COOKIE_AGE = 60 * 60 * 2

LOGIN_REDIRECT_URL = '/survey/thanks/'

MULTI_PROFILE_ALLOWED = 'false' #pekka

INTERNAL_IPS = PrivateIPs()
