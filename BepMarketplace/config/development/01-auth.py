#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#

## Login
LOGIN_REDIRECT_URL = '/' # after login go to homepage
LOGIN_URL = '/login/'
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
# SHEN_RING_URL = "https://shen.ele.tue.nl/"
# SHEN_RING_NO_CSRF = False
# SHEN_RING_CLIENT_ID = SHEN_RING_CLIENT_ID
# SHEN_RING_CLIENT_SECRET = SHEN_RING_CLIENT_SECRET

# OIDC settings
# URLS From : https://connect.surfconext.nl/.well-known/openid-configuration
# LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
OIDC_CALLBACK_CLASS = 'mozilla_django_oidc_custom.views.CustomOIDCAuthenticationCallbackView'
# OIDC_AUTHENTICATE_CLASS = ''
OIDC_OP_AUTHORIZATION_ENDPOINT = "https://connect.surfconext.nl/oidc/authorize"
OIDC_OP_TOKEN_ENDPOINT = "https://connect.surfconext.nl/oidc/token"
OIDC_OP_USER_ENDPOINT = "https://connect.surfconext.nl/oidc/userinfo"
OIDC_PROXY = {'https': 'http://proxy.tue.nl:3128'}
OIDC_RP_SIGN_ALGO= 'RS256'
OIDC_OP_JWKS_ENDPOINT = 'https://connect.surfconext.nl/oidc/certs'
