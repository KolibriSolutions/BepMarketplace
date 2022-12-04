#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from BepMarketplace.secret import IMPORT_EMAIL_HOST_PASSWORD

EMAIL_HOST = 'smtp.office365.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'svcbepmarktplcmailer@tue.nl'
EMAIL_HOST_PASSWORD = IMPORT_EMAIL_HOST_PASSWORD
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
SERVER_EMAIL = 'bepmarketplace_mailer@tue.nl'
FROM_EMAIL_ADDRESS = SERVER_EMAIL
EMAIL_TIMOUT = 20  # seconds

# EMAIL_HOST = 'localhost'
# EMAIL_PORT = 1025
# EMAIL_HOST_USER = ''
# EMAIL_HOST_PASSWORD = ''
# EMAIL_USE_TLS = False
# SERVER_EMAIL = 'no-reply@localhost'
# FROM_EMAIL_ADDRESS = SERVER_EMAIL
