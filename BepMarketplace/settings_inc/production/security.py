LOGIN_REDIRECT_URL = '/' # after login go to homepage

ALLOWED_HOSTS = (HOSTNAME,)  # where requests can come from

SESSION_COOKIE_AGE = 86400  # one day
SESSION_COOKIE_SECURE = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
# cached sessions: disabled because SAML2 does not support it
# SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'

CSRF_USE_SESSIONS = True  # do not use cookies for csrf

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

# Impersonate
IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True

# SSL
# Nginx should have:  proxy_set_header X-Forwarded-Protocol https;
# to let django know it is https using the next setting:
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTOCOL', 'https')
# To make sure it isn't forgotten to set this header, redirect to bullshit domain if it fails.
SECURE_SSL_REDIRECT = True  # if x_forwarde_protocol fails, redirect to:
SECURE_SSL_HOST = 'the-nginx-config-is-failing.test'

SECURE_HSTS_SECONDS = 86400*7  # 7 days
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True