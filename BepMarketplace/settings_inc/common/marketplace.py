
# General settings for the projects
####################################
MAX_NUM_APPLICATIONS = 5              # number of applications a student can have.
EMAILREGEXCHECK = '(^[a-zA-Z0-9]{1}[a-zA-Z0-9_.+-~]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)'  # regex that checks for email.
MAX_UPLOAD_SIZE = 10*1024*1024  # max size of any uploaded file 10MB. This limit should be lower than the NGINX limit
MAXAGESHARELINK = 60*60*24*7
ALLOWED_PROPOSAL_ATTACHEMENTS = ['pdf']
ALLOWED_PROPOSAL_IMAGES = ['jpg', 'jpeg', 'png', 'bmp', 'gif']
ALLOWED_PUBLIC_FILES = ['pdf','jpg', 'jpeg', 'png', 'bmp', 'gif','doc','docx','xls','xlsx','odt','ods','odp','ppt','pptx','tex','txt','rtf']
ALLOWED_STUDENT_FILES = ALLOWED_PUBLIC_FILES
ALLOWED_PROPOSAL_ASSISTANT_DOMAINS = ['tue.nl', ]


# How long to cache models that are assumed static. (Group types, timeslots, timphases)
STATIC_OBJECT_CACHE_DURATION = 15*60  # 15 minutes.

