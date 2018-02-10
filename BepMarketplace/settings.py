"""
Django settings for BepMarketplace project.

Kolibri Solutions. Frank Boerman & Jeroen van Oorschot 2016-2018

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

import saml2
import saml2.saml

from BepMarketplace.secret import SECRET_KEY_IMPORT, DATABASE_PASSWORD_IMPORT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DJANGO settings
##################

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

CONTACT_EMAIL = 'bepmarketplace@tue.nl'
ADMINS = [('devteam', CONTACT_EMAIL)]
MANAGERS = ADMINS

NAME_CODE = 'BEPMarketplace'
NAME_PRETTY = 'BEP Marketplace'
HOSTNAME = 'bep.ele.tue.nl'
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
    'osirisdata.apps.OsirisdataConfig',

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
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # for superusers, and 2fa.
    'djangosaml2.backends.Saml2Backend', # for all users (TUE with single signon)
)

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'django',
        'USER' : 'django',
        'PASSWORD' : DATABASE_PASSWORD_IMPORT,
        'HOST' : 'localhost',
        'POST' : '',
        'CONN_MAX_AGE': 86400  # one day
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators
# only used for admin 2fa login
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
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT':None,
        'KEY_PREFIX': NAME_CODE,
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
        'saml_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/home/django/saml2.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {  # to disable mailing when invalid host header is accessed.
            'handlers': ['file'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # logging for saml
        'djangosaml2': {
             'handlers': ['saml_file', 'mail_admins'],
             'level': 'WARNING',
        },
        'saml2': {
             'handlers': ['saml_file'],
             'level': 'CRITICAL',  # to disable logging on unsolicitedresponses etc.
        },
    },
}
# the subject prefix for error emails.
EMAIL_SUBJECT_PREFIX = '[DJANGO '+NAME_CODE + ' ]'

# channels, a new and better way to run Django including websockets.
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgi_redis.RedisChannelLayer',
        'CONFIG': {
            'hosts': ['redis://127.0.0.1:6379/2'],
        },
        'ROUTING': SETTINGS_DIR + '.routing.channel_routing',
    },
}

# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Security
LOGIN_URL = '/login/'  # for saml login
LOGIN_REDIRECT_URL = '/'

DOMAIN = 'https://'+HOSTNAME  # also used for SAML metadata
IPWARE_TRUSTED_PROXY_LIST = []
ALLOWED_HOSTS = (HOSTNAME,)  # where requests can come from

# Nginx should have:  proxy_set_header X-Forwarded-Protocol https;
# to let django know it is https using the next setting:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
# To make sure it isn't forgotten to set this header, redirect to bullshit domain if it fails.
SECURE_SSL_REDIRECT = True  # if x_forwarde_protocol fails, redirect to:
SECURE_SSL_HOST = 'the-nginx-config-is-failing.test'

SESSION_COOKIE_AGE = 86400  # one day
SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# cached sessions: disabled because SAML2 does not support it
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CSRF_USE_SESSIONS = True  # do not use cookies for csrf

SECURE_HSTS_SECONDS = 86400*7  # 7 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # prevent mime-type sniffing
X_FRAME_OPTIONS = 'DENY'

CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")  # base64 images are used by lightbox
CSP_FONT_SRC = ("'self'", "https://themes.googleusercontent.com")  # metro uses google fonts.
CSP_CONNECT_SRC = ("'self'", "wss://"+HOSTNAME)  # websockets and ajax. Make sure wss:// is set and not ws://.
CSP_FRAME_ANCESTORS = ("'none'")
CSP_FORM_ACTION = ("'self'")  # where form action=URI can point to


# path for media upload. Media download is not available on this path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# copy static files from custom apps to the same static root as other files
STATIC_ROOT = '/home/django/BepMarketplace/templates/static/'


# Email is using a postfix smarthost, so these settings are not important
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
# 'from' emailadress
SERVER_EMAIL = 'no-reply@'+HOSTNAME
FROM_EMAIL_ADDRESS = SERVER_EMAIL


# Plugin options
#################

# path for media download. This uses auth via the sendfile backend.
SENDFILE_BACKEND = 'sendfile.backends.simple'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'

IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True

# Minify
HTML_MINIFY = True

# markdownx
MARKDOWNX_MARKDOWNIFY_FUNCTION = 'markdownx_custom.utils.markdownify_safe'

# General settings for the projects
####################################
MAX_NUM_APPLICATIONS = 5              # number of applications a student can have.
EMAILREGEXCHECK = '(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'  # regex that checks for email.
MAX_UPLOAD_SIZE = 10*1024*1024  # max size of any uploaded file 10MB. This limit should be lower than the NGINX limit
MAXAGESHARELINK = 60*60*24*7
ALLOWED_PROPOSAL_ATTACHEMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES
ALLOWED_PROPOSAL_ASSISTANT_DOMAINS = ['tue.nl', ]

# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15*60  # 15 minutes.


# SAML
#######

SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': DOMAIN + '/saml2/metadata/',

    # To let us use any attribute that the SAML data contains.
    'allow_unknown_attributes': True,

    # Probably not needed:
    # directory with attribute mapping
    # 'attribute_map_dir': path.join(BASE_DIR, 'attribute-maps'),

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp': {
            'name': NAME_CODE,
            'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    (DOMAIN + '/saml2/acs/', saml2.BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    (DOMAIN + '/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
                    (DOMAIN + '/saml2/ls/post', saml2.BINDING_HTTP_POST),
                ],
            },
            'allow_unsolicited': False, # disable to stop replay attack.
            # These don't seem to be needed:

            # attributes that this project need to identify a user
            #'required_attributes': [''],

            # attributes that may be useful to have but not required
            #'optional_attributes': [''],

            # in this section the list of IdPs we talk to are defined
            # NOT USED, see https://github.com/knaperek/djangosaml2/issues/116
            # 'idp': {
            #     # we do not need a WAYF service since there is
            #     # only an IdP defined here. This IdP should be
            #     # present in our metadata
            #     'https://sts.tue.nl': {
            #         'single_sign_on_service': {
            #             saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/IDPInitiatedSignon.aspx?LoginToRP=' + DOMAIN + '/',
            #         },
            #         'single_logout_service': {
            #             saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/?wa=wsignout1.0',
            #         },
            #     },
            #},
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
         'company': 'Kolibri Solutions',
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

SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email' # Use email to match saml users to django users
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKOWN_USER = True
SAML_USE_NAME_ID_AS_USERNAME = False
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT
# all other mappings (the less simple ones) are done in djangosaml2_custom/signals/handler.py
SAML_ATTRIBUTE_MAPPING = {
    'urn:mace:dir:attribute-def:uid': ('username', ),
    'urn:mace:dir:attribute-def:mail': ('email', ),
}
SAML_ACS_FAILURE_RESPONSE_FUNCTION = 'djangosaml2_custom.acs_failures.template_failure'
