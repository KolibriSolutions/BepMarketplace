import os
import binascii
import os.path

if os.path.isfile("BepMarketplace/secret.py"):
    print("secret file already exists!")
else:
    key = binascii.hexlify(os.urandom(24)).decode()
    with open("BepMarketplace/secret.py", "w") as stream:
        stream.write("SECRET_KEY_IMPORT = '{}'\nDATABASE_PASSWORD_IMPORT = 'banaan'".format(key))
    print("secret file generated")

