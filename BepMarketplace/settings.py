import os

conffiles = [
    'BepMarketplace/config/common/01-marketplace.py',
    'BepMarketplace/config/common/02-base.py',
    'BepMarketplace/config/common/03-security.py',

    'BepMarketplace/config/production/01-auth.py',
    'BepMarketplace/config/production/02-database.py',
    'BepMarketplace/config/production/03-email.py',
    'BepMarketplace/config/production/05-logging.py',
]

DEBUG = False
HOSTNAME = 'bep.ele.tue.nl'

for f in conffiles:
    fo = open(os.path.abspath(f))
    exec(fo.read())
    fo.close()

# in case of overridessa
DEBUG = False
