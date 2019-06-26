import os
import binascii
import os.path

if os.path.isfile("BepMarketplace/secret.py"):
    print("secret file already exists!")
else:
    key = binascii.hexlify(os.urandom(24)).decode()
    with open("BepMarketplace/secret.py", "w") as stream:
        stream.write("PYLTI_CONFIG = {{}}\nSECRET_KEY_IMPORT = '{}'\nSHEN_RING_CLIENT_ID=\"\"\nSHEN_RING_CLIENT_SECRET=\"\"\nDATABASE_PASSWORD_IMPORT = 'banaan'".format(key))
    print("secret file generated")

