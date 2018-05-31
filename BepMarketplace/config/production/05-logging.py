# Log to a logfile and send errors to the devteam.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/django/django.log',
        },
        'saml_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': '/home/django/saml2.log',
        },
        'js_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/home/django/js_error.log',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        },
    },
    'loggers': {
        'django.security.DisallowedHost': {  # to disable mailing when invalid host header is accessed.
            'handlers': ['file'],
            'propagate': False,
            'level': 'CRITICAL',
        },
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
        # logging for saml
        'djangosaml2': {
             'handlers': ['saml_file', 'mail_admins'],
             'level': 'WARNING',
        },
        'saml2': {
             'handlers': ['saml_file'],
             'level': 'CRITICAL',  # to disable logging on unsolicitedresponses etc.
        },
        'javascript_error': {
            'handlers': ['mail_admins', 'js_file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
# the subject prefix for error emails.
EMAIL_SUBJECT_PREFIX = '[DJANGO '+NAME_CODE + ' ]'

