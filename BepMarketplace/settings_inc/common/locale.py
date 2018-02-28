
# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'en-US'
TIME_ZONE = 'Europe/Amsterdam'
USE_I18N = False  # translation backend, not used, so False.
USE_L10N = False # number formatting based on user's browser locale
USE_TZ = True

# overrides (only used if USE_L10N is False)
DATE_FORMAT = 'N j, Y'
SHORT_DATE_FORMAT = 'd-m-Y'
DATETIME_FORMAT = 'N j, Y, H:i'
SHORT_DATETIME_FORMAT = 'd-m-Y H:i'
