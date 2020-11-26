#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
#

import binascii
import os.path

# secrets file with passwords.
if os.path.isfile("BepMarketplace/secret.py"):
    print("secret file already exists!")
else:
    key = binascii.hexlify(os.urandom(24)).decode()
    with open("BepMarketplace/secret.py", "w") as stream:
        stream.write(
            "PYLTI_CONFIG = {{}}\nSECRET_KEY_IMPORT = '{}'\nSHEN_RING_CLIENT_ID=\"\"\nSHEN_RING_CLIENT_SECRET=\"\"\nDATABASE_PASSWORD_IMPORT = 'banaan'\n".format(
                key))
    print("secret file generated")

# 01-marketplace settings file with application specific information
if os.path.isfile("BepMarketplace/config/common/01-marketplace.py"):
    print("marketplace settings file already exists!")
else:
    os.rename('BepMarketplace/config/common/01-marketplace.py.example', 'BepMarketplace/config/common/01-marketplace.py')
    print("example marketplace settings file 01-marketplace.py moved.")