#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
## DJANGO SETTTINGS

## 01-marketplace.py
## Settings specific for this marketplace instance
if DEBUG:
    HOSTNAME = 'localhost'
else:
    HOSTNAME = 'bep.ele.tue.nl'

# contact email, shown on some pages and in case of errors (500)
CONTACT_EMAIL = 'bepmarketplace@tue.nl'

# responsible person for the system, shown on homepage.
SUPPORT_ROLE = 'responsible teacher'
SUPPORT_NAME = 'Maarten adsf'
SUPPORT_EMAIL = 'asdf@tue.nl'

# for mailing errors and such
DEV_EMAIL = 'bepmarketplace@kolibrisolutions.nl'
ADMINS = [('Kolibri Solutions', DEV_EMAIL)]
MANAGERS = ADMINS  # to mail broken links to, not used now.

# name as visible on some pages and emails.
NAME_CODE = 'BEPMarketplace'
NAME_PRETTY = 'BEP Marketplace'

# used for canvas integration
COURSE_CODE_EXT = "5XED0"
COURSE_CODE_BEP = "5XEC0"

# used for studyguide capacitygroup detail link to mastermp. Not required, remove if not used.
MASTERMARKETPLACE_URL = 'https://master.ele.tue.nl'


# General settings for the projects
####################################

# quantization factor for the final grades in the grading system.
CATEGORY_GRADE_QUANTIZATION = 0.25

MAX_NUM_APPLICATIONS = 5              # number of applications a student can have.
MAX_UPLOAD_SIZE = 10*1024*1024  # max size of any uploaded file 10MB. This limit should be lower than the NGINX limit
MAXAGESHARELINK = 60*60*24*7

ALLOWED_PROJECT_ATTACHMENTS = ['pdf']  # allowed files for project attachments
ALLOWED_PROPOSAL_ATTACHMENTS = ALLOWED_PROJECT_ATTACHMENTS
ALLOWED_PROJECT_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']  # allowed files as project images.
ALLOWED_PROPOSAL_IMAGES = ALLOWED_PROJECT_IMAGES
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES
# to check when a user is staff on saml login.
STAFF_EMAIL_DOMAINS = ['tue.nl', ]
# to check whether a email address can be used to add an assistant
ALLOWED_PROJECT_ASSISTANT_DOMAINS = STAFF_EMAIL_DOMAINS
ALLOWED_PROPOSAL_ASSISTANT_DOMAINS = ALLOWED_PROJECT_ASSISTANT_DOMAINS
STUDENT_EMAIL_DOMAINS = ['student.tue.nl', ]
ALLOWED_PRIVATE_STUDENT_DOMAINS = STUDENT_EMAIL_DOMAINS

# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15 * 60  # 15 minutes.
