
==================
djangosaml2_custom
==================

This app contains some custom code for interfacing with djangosaml2 for the saml/adfs login system. It overwrites the
ACS function in views.py, to be able to parse custom user attributes and custom checks whether a user is allowed to
login.

****
Code
****

.. toctree::
    :name: djangosaml2_custom

    views