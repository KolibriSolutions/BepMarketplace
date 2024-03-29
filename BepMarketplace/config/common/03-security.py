#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

ALLOWED_HOSTS = (HOSTNAME,)  # where requests can come from
CSRF_TRUSTED_ORIGINS = ['https://' + HOSTNAME]

## Sessions
SESSION_COOKIE_AGE = 86400  # one day
SESSION_COOKIE_SECURE = not DEBUG
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'


## Filters
CSRF_USE_SESSIONS = True  # do not use cookies for csrf
CSRF_FAILURE_VIEW = 'index.views.csrf_failure'
# error handler for other errors is set in root urlconf.

SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True  # prevent mime-type sniffing
CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'")
CSP_IMG_SRC = ("'self'", "data:")  # base64 images are used by lightbox
CSP_CONNECT_SRC = ("'self'", "wss://"+HOSTNAME)  # websockets and ajax. Make sure wss:// is set and not ws://.
CSP_BASE_URI = ("'self'")
CSP_FRAME_ANCESTORS = ("https://canvas.tue.nl https://eindhoven.instructure.com")  # Allow is being inherited by canvas in iframe.
CSP_FORM_ACTION = ("'self'")  # where form action=URI can point to

## Impersonate
# impersonate is by default enabled for staff users. If a type3 is allowed to impersonate, the is_staff should be set in admin.
IMPERSONATE = {
    'REQUIRE_SUPERUSER': False,
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
# path for media download. This uses auth via the sendfile backend. Backend is set in 02-database.py
SENDFILE_ROOT = MEDIA_ROOT
SENDFILE_URL = '/media/'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
if not DEBUG:
    ## SSL
    # Nginx should have:  proxy_set_header X-Forwarded-Protocol https;
    # to let django know it is https using the next setting:
    # SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
    # To make sure it isn't forgotten to set this header, redirect to bullshit domain if it fails.
    SECURE_HSTS_SECONDS = 63072000  # half year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
