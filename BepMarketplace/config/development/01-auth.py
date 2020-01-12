#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from BepMarketplace.secret import SHEN_RING_CLIENT_ID, SHEN_RING_CLIENT_SECRET

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
SHEN_RING_URL = "https://shen.ele.tue.nl/"
SHEN_RING_NO_CSRF = False
SHEN_RING_CLIENT_ID = SHEN_RING_CLIENT_ID
SHEN_RING_CLIENT_SECRET = SHEN_RING_CLIENT_SECRET
