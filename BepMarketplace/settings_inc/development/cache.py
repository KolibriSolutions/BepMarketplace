# cache
CACHES = {
    'default':{
        #'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'asgiref.inmemory.ChannelLayer',
        'ROUTING': SETTINGS_DIR + '.routing.channel_routing',
    },
}

HTML_MINIFY = False
