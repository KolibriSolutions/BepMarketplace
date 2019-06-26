from BepMarketplace.secret import SHEN_RING_CLIENT_ID, SHEN_RING_CLIENT_SECRET

## Login
LOGIN_REDIRECT_URL = '/' # after login go to homepage
LOGIN_URL = '/login/'  # for saml login
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # for superusers, and 2fa.
    # 'djangosaml2.backends.Saml2Backend', # for all users (TUE with single signon)
)

# Password validation
# only used for admin 2fa login
AUTH_PASSWORD_VALIDATORS = [
]

# shen ring settings
# SHEN_RING_URL = "http://localhost:8000/"
SHEN_RING_URL = "https://shen.ele.tue.nl/"
SHEN_RING_NO_CSRF = False