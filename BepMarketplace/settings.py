import os

conffiles = [
     'BepMarketplace/settings_inc/common/base.py'
,    'BepMarketplace/settings_inc/common/locale.py'
,    'BepMarketplace/settings_inc/common/marketplace.py'
    
,    'BepMarketplace/settings_inc/production/auth.py'
,    'BepMarketplace/settings_inc/production/cache.py'
,    'BepMarketplace/settings_inc/production/database.py'
,    'BepMarketplace/settings_inc/production/email.py'
,    'BepMarketplace/settings_inc/production/logging.py'
,    'BepMarketplace/settings_inc/production/media.py'
,    'BepMarketplace/settings_inc/production/production.py'
,    'BepMarketplace/settings_inc/production/saml.py'
,    'BepMarketplace/settings_inc/production/security.py'
]

for f in conffiles:
    exec(open(os.path.abspath(f)).read())