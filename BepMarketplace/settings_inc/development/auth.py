AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # for superusers, and 2fa.
    # 'djangosaml2.backends.Saml2Backend', # for all users (TUE with single signon)
)

# Password validation
# only used for admin 2fa login
AUTH_PASSWORD_VALIDATORS = [
]

LOGIN_URL = '/two_factor/login/'
