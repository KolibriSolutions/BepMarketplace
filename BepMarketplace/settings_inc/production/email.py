# Email is using a postfix smarthost, so these settings are not important
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
# 'from' emailadress
SERVER_EMAIL = 'no-reply@'+HOSTNAME
FROM_EMAIL_ADDRESS = SERVER_EMAIL
