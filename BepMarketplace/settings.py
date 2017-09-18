"""
Django settings for BepMarketplace project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
from os import path
import saml2
import saml2.saml
from BepMarketplace.secret import SECRET_KEY_IMPORT, DATABASE_PASSWORD_IMPORT
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ("*",)
ADMINS = [("devteam", "bepmarketplace@tue.nl")]

# LOGIN_URL = "/login/"
LOGIN_URL = '/saml2/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

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
    'impersonate',
    'maintenancemode',
    'channels',
    'sendfile',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'djangosaml2',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'htmlmin.middleware.HtmlMinifyMiddleware',
    'htmlmin.middleware.MarkRequestMiddleware',
    'tracking.middleware.TelemetryMiddleware'
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # for superusers, and 2fa.
    'djangosaml2.backends.Saml2Backend', # for all users (TUE with single signon)
)

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'django',
        'USER' : 'django',
        'PASSWORD' : DATABASE_PASSWORD_IMPORT,
        'HOST' : 'localhost',
        'POST' : ''
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Use REDIS to cache certain pages and variables.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "TIMEOUT":None,
        "KEY_PREFIX":"bepmarketplacedev",
    }
}

# Log to a logfile and send errors to the devteam.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/django/django.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file','mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# cached sessions: disabled because SAML2 does not support it
# SESSION_ENGINE = "django.contrib.sessions.backends.cached_db"

# channels, a new and better way to run Django including websockets.
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "asgi_redis.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["redis://127.0.0.1:6379/2"],
        },
        "ROUTING": "BepMarketplace.routing.channel_routing",
    },
}


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

#the domain on which it is run
DOMAIN = "https://bep.ele.tue.nl"
#email on which the team is reachable
CONTACT_EMAIL = "bepmarketplace@tue.nl"
#noreply address from wich to mail
NOREPLY_EMAIL = "noreply@bep.ele.tue.nl"

# path for media upload. Media download is not available on this path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'

# path for media download. This uses auth via the sendfile backend.
# SENDFILE settings
#SENDFILE_BACKEND = 'sendfile.backends.development'
#SENDFILE_BACKEND = 'sendfile.backends.xsendfile'
#SENDFILE_BACKEND = 'sendfile.backends.nginx'
SENDFILE_BACKEND = 'sendfile.backends.simple'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = '/static/'
STATIC_ROOT = '/home/django/templates/static/'


# Host for sending e-mail.
EMAIL_HOST = 'localhost'
# Port for sending e-mail.
EMAIL_PORT = 25
# Optional SMTP authentication information for EMAIL_HOST.
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False

SESSION_COOKIE_AGE = 86400
LOGIN_REDIRECT_URL = '/'
IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True
MAINTENANCE_MODE = False

# General settings for the BEPs.
MAX_NUM_APPLICATIONS = 5
MAXAGESHARELINK = 60*60*24*7
EMAILREGEXCHECK = "(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
MAX_UPLOAD_SIZE = 10*1024*1024 #10MB
ALLOWED_PROPOSAL_ATTACHEMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']

# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15*60  # 15 minutes.

#login security
MAX_FAIL_LOGIN_NUM = 5
LOCKOUT_TIME = 15*60
IPWARE_TRUSTED_PROXY_LIST = []

#SAML
SAML_CONFIG = {
  # full path to the xmlsec1 binary programm
  'xmlsec_binary': '/usr/bin/xmlsec1',

  # your entity id, usually your subdomain plus the url to the metadata view
  'entityid': DOMAIN+'/saml2/metadata/',

    #To let us use any attribute that the SAML data contains.
  'allow_unknown_attributes': True,

  # Probably not needed:
  # directory with attribute mapping
  # 'attribute_map_dir': path.join(BASE_DIR, 'attribute-maps'),

  # this block states what services we provide
  'service': {
      # we are just a lonely SP
      'sp' : {
          'name': 'ieeesb',
          'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
          'endpoints': {
              # url and binding to the assetion consumer service view
              # do not change the binding or service name
              'assertion_consumer_service': [
                  (DOMAIN+'/saml2/acs/',
                   saml2.BINDING_HTTP_POST),
                  ],
              # url and binding to the single logout service view
              # do not change the binding or service name
              'single_logout_service': [
                  (DOMAIN+'/saml2/ls/',
                   saml2.BINDING_HTTP_REDIRECT),
                  (DOMAIN+'/saml2/ls/post',
                   saml2.BINDING_HTTP_POST),
                  ],
              },

          # These don't seem to be needed:

          # attributes that this project need to identify a user
          #'required_attributes': [''],

          # attributes that may be useful to have but not required
          #'optional_attributes': [''],

          # in this section the list of IdPs we talk to are defined
          'idp': {
              # we do not need a WAYF service since there is
              # only an IdP defined here. This IdP should be
              # present in our metadata
              'https://sts.tue.nl/adfs/ls/': {
                  'single_sign_on_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/IDPInitiatedSignon.aspx?LoginToRP='+DOMAIN+'/',
                      },
                  'single_logout_service': {
                      saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/?wa=wsignout1.0',
                      },
                  },
              },
          },
      },

  # where the remote metadata is stored
  'metadata': {
      'local': ['/home/django/tuemetadata.xml'],
      },

  # set to 1 to output debugging information
  'debug': 0,

  # Signing
  'key_file': '/home/django/certs/faraday.key',  # private part
  'cert_file': '/home/django/certs/faraday_ele_tue_nl.crt',  # public part
# Encryption
  'encryption_keypairs': [{
      'key_file': '/home/django/certs/faraday.key',  # private part
      'cert_file': '/home/django/certs/faraday_ele_tue_nl.crt',  # public part
  }],

  # own metadata settings
  'contact_person': [
      {'given_name': 'Frank',
       'sur_name': 'Boerman',
       'company': 'ELE TU/e',
       'email_address': CONTACT_EMAIL,
       'contact_type': 'technical'},
      {'given_name': 'Sjoerd',
       'sur_name': 'Hulshof',
       'company': 'ELE TU/e',
       'email_address': 's.hulshof@tue.nl',
       'contact_type': 'administrative'},
      ],
  'valid_for': 24,  # how long is our metadata valid, needs to be short because letsencrypt certs
  }

#SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email' # nameID is used as username.
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKOWN_USER = True
SAML_USE_NAME_ID_AS_USERNAME = True
# Not used, because custom ACS is used in djangosaml2_custom.views
#SAML_ATTRIBUTE_MAPPING = {
#}

HTML_MINIFY = True
