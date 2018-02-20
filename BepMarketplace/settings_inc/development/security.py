LOGIN_REDIRECT_URL = '/' # after login go to homepage

ALLOWED_HOSTS = ('localhost',)  # where requests can come from

SESSION_COOKIE_AGE = 86400  # one day
SESSION_COOKIE_SECURE = False  # because non-https in dev.
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
CSP_CONNECT_SRC = ("'self'", "ws://localhost:*")  # websockets and ajax. Make sure wss:// is set and not ws://.
CSP_FRAME_ANCESTORS = ("'none'")
CSP_FORM_ACTION = ("'self'")  # where form action=URI can point to

# Impersonate
IMPERSONATE_REQUIRE_SUPERUSER = True
IMPERSONATE_DISABLE_LOGGING = True