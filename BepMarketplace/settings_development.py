import os

conffiles = [
    'BepMarketplace/config/common/01-marketplace.py',
    'BepMarketplace/config/common/02-base.py',
    'BepMarketplace/config/common/03-security.py',

    'BepMarketplace/config/development/01-auth.py',
    'BepMarketplace/config/development/02-database.py',
    'BepMarketplace/config/development/03-email.py',
    'BepMarketplace/config/development/10-overrides.py',
]

DEBUG = True
HOSTNAME = 'localhost'

for f in conffiles:
    fo = open(os.path.abspath(f))
    exec(fo.read())
    fo.close()


#  needed for pycharm to detect installed apps in templates. Only for debugging purposes.
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
    'canvas.apps.CanvasConfig',

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
    'django_js_error_hook',
]
