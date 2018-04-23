## DJANGO SETTTINGS

## 01-marketplace.py
## Settings specific for this marketplace instance


import os

try:
    from BepMarketplace.config.secret import SECRET_KEY_IMPORT
except:
    from BepMarketplace.secret import SECRET_KEY_IMPORT

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# DJANGO settings
##################

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY_IMPORT

SETTINGS_DIR = 'BepMarketplace'

CONTACT_EMAIL = 'bepmarketplace@tue.nl'
DEV_EMAIL = 'bepmarketplace@kolibrisolutions.nl'

ADMINS = [('Kolibri Solutions', DEV_EMAIL)]
MANAGERS = ADMINS  # to mail broken links to, not used now.

NAME_CODE = 'BEPMarketplace'
NAME_PRETTY = 'BEP Marketplace'


# General settings for the projects
####################################
MAX_NUM_APPLICATIONS = 5              # number of applications a student can have.
EMAILREGEXCHECK = '(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'  # regex that checks for email.
MAX_UPLOAD_SIZE = 10*1024*1024  # max size of any uploaded file 10MB. This limit should be lower than the NGINX limit
MAXAGESHARELINK = 60*60*24*7
ALLOWED_PROPOSAL_ATTACHMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES
ALLOWED_PROPOSAL_ASSISTANT_DOMAINS = ['tue.nl', ]
ALLOWED_PRIVATE_STUDENT_DOMAINS = ['student.tue.nl', ]


# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15*60  # 15 minutes.


# Application definition
INSTALLED_APPS = [
    'api.apps.ApiConfig',
    'distributions.apps.DistributionsConfig',
    'djangosaml2_custom.apps.Djangosaml2CustomConfig',
    'download.apps.DownloadConfig',
    'godpowers.apps.GodpowersConfig',
    'index.apps.IndexConfig',
    'presentations.apps.PresentationsConfig',
    'professionalskills.apps.ProfessionalskillsConfig',
    'proposals.apps.ProposalsConfig',
    'results.apps.ResultsConfig',
    'students.apps.StudentsConfig',
    'support.apps.SupportConfig',
    'templates.apps.TemplatesConfig',
    'timeline.apps.TimelineConfig',
    'tracking.apps.TrackingConfig',
    'two_factor_custom.apps.TwoFactorCustomConfig',
    'osirisdata.apps.OsirisdataConfig',

    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',

    'channels',
    'csp',
    'djangosaml2',
    'impersonate',
    'openpyxl',
    'sendfile',
    'two_factor',
]
