#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

ALLOWED_HOSTS = (HOSTNAME,)  # where requests can come from


## Sessions
SESSION_COOKIE_AGE = 86400  # one day
SESSION_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# cached sessions: disabled because SAML2 does not support it
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


## Filters
CSRF_USE_SESSIONS = True  # do not use cookies for csrf
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # prevent mime-type sniffing
X_FRAME_OPTIONS = 'allow-from https://canvas.tue.nl'  # superseded by CPS_FRAME_ANCESTORS, only for backwards compat.
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")  # base64 images are used by lightbox
CSP_CONNECT_SRC = ("'self'", "wss://"+HOSTNAME)  # websockets and ajax. Make sure wss:// is set and not ws://.
CSP_BASE_URI = ("'self'")
CSP_FRAME_ANCESTORS = ("https://canvas.tue.nl")  # Allow is being inherited by canvas in iframe.
CSP_FORM_ACTION = ("'self'")  # where form action=URI can point to

## Impersonate
IMPERSONATE = {
    'REQUIRE_SUPERUSER': True,
    'DISABLE_LOGGING': True,
}


## Media
MARKDOWN_IMAGE_UPLOAD_FOLDER = 'markdown'
# path for media upload. Media download is not available on this path.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/download/'
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# copy static files from custom apps to the same static root as other files
STATIC_ROOT = os.path.join(BASE_DIR, 'templates/static')
# path for media download. This uses auth via the sendfile backend.
SENDFILE_BACKEND = 'sendfile.backends.simple'
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/protected/'

if not DEBUG:
    SECURE_HSTS_SECONDS = 63072000  # half year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

## shen
USERMETA_LOCAL_FIELDS = ['ECTS', 'EnrolledBEP', 'EnrolledExt', 'Overruled', 'Studentnumber']
