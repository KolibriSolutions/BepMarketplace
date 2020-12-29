#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import os

LOG_DIR = os.path.join(BASE_DIR, 'logging')

# Log to a logfile and send errors to the devteam.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {filename}:{lineno} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'saml_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOG_DIR, 'saml2.log'),
            'formatter': 'verbose',
        },
        # 'js_file': {
        #     'level': 'ERROR',
        #     'class': 'logging.FileHandler',
        #     'filename': os.path.join(LOG_DIR, 'js_error.log'),
        #     'formatter': 'verbose',
        # },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'formatter': 'verbose',
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
        # 'javascript_error': {
        #     'handlers': ['js_file'],
        #     'level': 'ERROR',
        #     'propagate': True,
        # },
    },
}
# the subject prefix for error emails.
EMAIL_SUBJECT_PREFIX = '[DJANGO ' + NAME_CODE + ' ]'
