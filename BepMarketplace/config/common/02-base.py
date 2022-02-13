#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
## DJANGO SETTTINGS

## 02-base.py
## Common settings for all django projects in development and production
import os

try:
    from BepMarketplace.config.secret import *
except:
    from BepMarketplace.secret import *

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TESTING = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

SETTINGS_DIR = 'BepMarketplace'

DOMAIN = 'https://'+HOSTNAME  # also used for SAML metadata

# django-ipware, used in tracking.
IPWARE_TRUSTED_PROXY_LIST = []

# django-js-error-hook, fix for csrf failure on post
JAVASCRIPT_ERROR_CSRF_EXEMPT = True

# django 3.2 default
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'  # 'django.db.models.AutoField'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'csp.middleware.CSPMiddleware',

    'impersonate.middleware.ImpersonateMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'tracking.middleware.TelemetryMiddleware',
    'index.middleware.TermsMiddleware'
]

ROOT_URLCONF = SETTINGS_DIR + '.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'templates.context_processors.debugsetting',
                'templates.context_processors.general',
            ],
            #  'string_if_invalid': '!VARIABLE ERROR IN TEMPLATE ("%s") !'  # enable to debug template variables
        },
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = False  # translation backend, not used, so False.
USE_L10N = False  # number formatting based on user's browser locale
USE_TZ = True

# overrides (only used if USE_L10N is False)
DATE_FORMAT = 'N j, Y'
SHORT_DATE_FORMAT = 'd-m-Y'
DATETIME_FORMAT = 'N j, Y, H:i'
SHORT_DATETIME_FORMAT = 'd-m-Y H:i'

# Application definition
INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'distributions.apps.DistributionsConfig',
    'download.apps.DownloadConfig',
    'godpowers.apps.GodpowersConfig',
    'index.apps.IndexConfig',
    'presentations.apps.PresentationsConfig',
    'professionalskills.apps.ProfessionalskillsConfig',
    'proposals.apps.ProposalsConfig',
    'results.apps.ResultsConfig',
    'students.apps.StudentsConfig',
    'support.apps.SupportConfig',
    'templates.apps.TemplatesConfig',
    'timeline.apps.TimelineConfig',
    'tracking.apps.TrackingConfig',
    'two_factor_custom.apps.TwoFactorCustomConfig',
    'osirisdata.apps.OsirisdataConfig',
    'canvas.apps.CanvasConfig',
    'shen_ring.apps.ShenRingConfig',

    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',

    'channels',
    'csp',
    'impersonate',
    'openpyxl',
    'sendfile',
    'two_factor',
    # 'django_js_error_hook',
]
