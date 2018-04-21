from BepMarketplace.config.secret import DATABASE_PASSWORD_IMPORT

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

# Use REDIS to cache certain pages and variables.
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'TIMEOUT': None,
        'KEY_PREFIX': NAME_CODE,
    }
}

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

HTML_MINIFY = True