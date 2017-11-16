"""
Django development settings for MasterMarketplace project.

Kolibri Solutions. Frank Boerman & Jeroen van Oorschot 2016-2018

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
from BepMarketplace.secret import SECRET_KEY_IMPORT
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DJANGO settings
##################

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
CONTACT_EMAIL = 'bepmarketplace@tue.nl'
ADMINS = [('devteam', CONTACT_EMAIL)]
MANAGERS = ADMINS

NAME_CODE = 'BepMarketplace'
NAME_PRETTY = 'BEP marketplace'
HOSTNAME = 'localhost'
SETTINGS_DIR = 'BepMarketplace'

# Application definition
INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'distributions.apps.DistributionsConfig',
    'djangosaml2_custom.apps.Djangosaml2CustomConfig',
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
    'djangosaml2',
    'impersonate',
    'openpyxl',
    'sendfile',
    'two_factor',
#    'debug_toolbar',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
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
                # 'templates.context_processors.debugsetting'
            ],
        },
    },
]

WSGI_APPLICATION = SETTINGS_DIR + '.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    # {
    #     'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    # },
    # {
    #     'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    # },
]

#cache
CACHES = {
    'default':{
        #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

#channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgiref.inmemory.ChannelLayer',
        'ROUTING': SETTINGS_DIR + '.routing.channel_routing',
    },
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Security
LOGIN_URL = '/two_factor/login/'
LOGIN_REDIRECT_URL = '/'

DOMAIN = 'http://'+HOSTNAME  # also used for SAML metadata
IPWARE_TRUSTED_PROXY_LIST = []
ALLOWED_HOSTS = (HOSTNAME, '*')  # where requests can come from

SESSION_COOKIE_AGE = 86400  # one day
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_USE_SESSIONS = True  # do not use cookies for csrf

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # prevent mime-type sniffing
X_FRAME_OPTIONS = 'DENY'

CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")  # base64 images are used by lightbox
CSP_FONT_SRC = ("'self'", "https://themes.googleusercontent.com")  # metro uses google fonts.
CSP_CONNECT_SRC = ("'self'", "ws://" + HOSTNAME + ':*')  # websockets and ajax. Make sure wss:// is set and not ws://.
CSP_FRAME_ANCESTORS = ("'none'")
CSP_FORM_ACTION = ("'self'")  # where form action=URI can point to


# path for media upload. Media download is not available on this path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, '../templates/static/')

# Assuming mailcatcher running localhost, https://mailcatcher.me/
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
# 'from' emailadress
SERVER_EMAIL = 'no-reply@'+HOSTNAME
FROM_EMAIL_ADDRESS = SERVER_EMAIL


# Plugin options
#################

# path for media download. This uses auth via the sendfile backend.
SENDFILE_BACKEND = 'sendfile.backends.development'
#SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
#SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'

IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True

# Minify
HTML_MINIFY = False

# markdownx
MARKDOWNX_MARKDOWNIFY_FUNCTION = 'markdownx_custom.utils.markdownify_safe'

# General settings for the projects
####################################
MAX_NUM_APPLICATIONS = 5              # number of applications a student can have.
MAXAGESHARELINK = 60*60*24*7
EMAILREGEXCHECK = '(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'
MAX_UPLOAD_SIZE = 10*1024*1024 #10MB
ALLOWED_PROPOSAL_ATTACHEMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES
ALLOWED_PROPOSAL_ASSISTANT_DOMAINS = ['tue.nl', ]

# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15*60  # 15 minutes.

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
 #   'debug_toolbar.panels.staticfiles.StaticFilesPanel', # this one fails
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
]