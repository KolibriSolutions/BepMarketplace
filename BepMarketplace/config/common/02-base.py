## DJANGO SETTTINGS

## 02-base.py
## Common settings for all django projects in development and production

DOMAIN = 'https://'+HOSTNAME  # also used for SAML metadata

# markdownx
MARKDOWNX_MARKDOWNIFY_FUNCTION = 'markdownx_custom.utils.markdownify_safe'

# django-ipware, used in tracking.
IPWARE_TRUSTED_PROXY_LIST = []

# django-js-error-hook, fix for csrf failure on post
JAVASCRIPT_ERROR_CSRF_EXEMPT = True

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
                # 'templates.context_processors.debugsetting',
                'templates.context_processors.general',
            ],
        },
    },
]

WSGI_APPLICATION = SETTINGS_DIR + '.wsgi.application'


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-US'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = False  # translation backend, not used, so False.
USE_L10N = False # number formatting based on user's browser locale
USE_TZ = True

# overrides (only used if USE_L10N is False)
DATE_FORMAT = 'N j, Y'
SHORT_DATE_FORMAT = 'd-m-Y'
DATETIME_FORMAT = 'N j, Y, H:i'
SHORT_DATETIME_FORMAT = 'd-m-Y H:i'
