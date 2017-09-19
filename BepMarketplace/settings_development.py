"""
Django settings for BepMarketplace project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'hivf+n&&eeu8f)!auby%m$6%zety+6dhw7g2f5y_@okkg@h)ec'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*','localhost:8080']
INTERNAL_IPS = ['127.0.0.1']
LOGIN_URL = "/login/"

# Application definition

INSTALLED_APPS = [
    'index.apps.IndexConfig',
    'templates.apps.TemplatesConfig',
    'proposals.apps.ProposalsConfig',
    'students.apps.StudentsConfig',
    'timeline.apps.TimelineConfig',
    'support.apps.SupportConfig',
    'api.apps.ApiConfig',
    'tracking.apps.TrackingConfig',
    'godpowers.apps.GodpowersConfig',
    'professionalskills.apps.ProfessionalskillsConfig',
    'presentations.apps.PresentationsConfig',
    'download.apps.DownloadConfig',
    'two_factor_custom.apps.TwoFactorCustomConfig',
    'djangosaml2_custom.apps.Djangosaml2CustomConfig',
    'results.apps.ResultsConfig',
    'distributions.apps.DistributionsConfig',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'openpyxl',
    'django_extensions',
    'impersonate',
    'channels',
    'sendfile',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
#    'debug_toolbar',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'tracking.middleware.TelemetryMiddleware',
    'index.middleware.TermsMiddleware'
]

ROOT_URLCONF = 'BepMarketplace.urls'

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
                'templates.context_processors.contactemail',
                'templates.context_processors.domain',
            ],
        },
    },
]

WSGI_APPLICATION = 'BepMarketplace.wsgi.application'


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
    "default": {
        "BACKEND": "asgiref.inmemory.ChannelLayer",
        "ROUTING": "BepMarketplace.routing.channel_routing",
    },
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#the domain on which it is run
DOMAIN = "http://localhost"
#email on which the team is reachable
CONTACT_EMAIL = "bepmarketplace@tue.nl"
#noreply address from wich to mail
NOREPLY_EMAIL = "noreply@bep.ele.tue.nl"
NAME_CODE = "BEPMarketplace"
NAME_PRETTY = "BEP marketplace"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'

# SENDFILE settings
SENDFILE_BACKEND = 'sendfile.backends.development'
#SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
#SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "../templates/static/")
MAX_NUM_APPLICATIONS = 5

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Host for sending e-mail.
EMAIL_HOST = 'localhost'

# Port for sending e-mail.
EMAIL_PORT = 1025

# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

SESSION_COOKIE_AGE = 86400
LOGIN_REDIRECT_URL = '/profile/'
IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True
MAXAGESHARELINK = 60*60*24*7
EMAILREGEXCHECK = "(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
MAX_UPLOAD_SIZE = 10*1024*1024 #10MB
ALLOWED_PROPOSAL_ATTACHEMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES

STATIC_OBJECT_CACHE_DURATION = 60  # 1 minute
#login security
MAX_FAIL_LOGIN_NUM = 5
LOCKOUT_TIME = 15*60

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

HTML_MINIFY = False