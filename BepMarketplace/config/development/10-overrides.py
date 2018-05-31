
# MIDDLEWARE.remove("htmlmin.middleware.HtmlMinifyMiddleware")

# to allow websockets in CSP over plain http
CSP_CONNECT_SRC = ("'self'", "ws://localhost:*")  # websockets and ajax. Make sure wss:// is set and not ws://.

# logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
         'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'javascript_error': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
