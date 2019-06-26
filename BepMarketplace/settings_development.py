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
