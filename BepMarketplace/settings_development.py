import os

conffiles = [
    'BepMarketplace/settings_inc/common/base.py'
    , 'BepMarketplace/settings_inc/common/locale.py'
    , 'BepMarketplace/settings_inc/common/marketplace.py'

    , 'BepMarketplace/settings_inc/development/auth.py'
    , 'BepMarketplace/settings_inc/development/cache.py'
    , 'BepMarketplace/settings_inc/development/database.py'
    , 'BepMarketplace/settings_inc/development/development.py'
    , 'BepMarketplace/settings_inc/development/email.py'
    , 'BepMarketplace/settings_inc/development/media.py'
    , 'BepMarketplace/settings_inc/development/security.py'
]

for f in conffiles:
    exec(open(os.path.abspath(f)).read())
