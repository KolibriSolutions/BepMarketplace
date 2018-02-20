import saml2

SAML_CONFIG = {
    # full path to the xmlsec1 binary programm
    'xmlsec_binary': '/usr/bin/xmlsec1',

    # your entity id, usually your subdomain plus the url to the metadata view
    'entityid': DOMAIN + '/saml2/metadata/',

    # To let us use any attribute that the SAML data contains.
    'allow_unknown_attributes': True,

    # Probably not needed:
    # directory with attribute mapping
    # 'attribute_map_dir': path.join(BASE_DIR, 'attribute-maps'),

    # this block states what services we provide
    'service': {
        # we are just a lonely SP
        'sp': {
            'name': NAME_CODE,
            'name_id_format': 'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
            'endpoints': {
                # url and binding to the assetion consumer service view
                # do not change the binding or service name
                'assertion_consumer_service': [
                    (DOMAIN + '/saml2/acs/', saml2.BINDING_HTTP_POST),
                ],
                # url and binding to the single logout service view
                # do not change the binding or service name
                'single_logout_service': [
                    (DOMAIN + '/saml2/ls/', saml2.BINDING_HTTP_REDIRECT),
                    (DOMAIN + '/saml2/ls/post', saml2.BINDING_HTTP_POST),
                ],
            },
            'allow_unsolicited': False, # disable to stop replay attack.
            # These don't seem to be needed:

            # attributes that this project need to identify a user
            #'required_attributes': [''],

            # attributes that may be useful to have but not required
            #'optional_attributes': [''],

            # in this section the list of IdPs we talk to are defined
            # NOT USED, see https://github.com/knaperek/djangosaml2/issues/116
            # 'idp': {
            #     # we do not need a WAYF service since there is
            #     # only an IdP defined here. This IdP should be
            #     # present in our metadata
            #     'https://sts.tue.nl': {
            #         'single_sign_on_service': {
            #             saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/IDPInitiatedSignon.aspx?LoginToRP=' + DOMAIN + '/',
            #         },
            #         'single_logout_service': {
            #             saml2.BINDING_HTTP_REDIRECT: 'https://sts.tue.nl/adfs/ls/?wa=wsignout1.0',
            #         },
            #     },
            #},
        },
    },

    # where the remote metadata is stored
    'metadata': {
        'local': ['/home/django/tuemetadata.xml'],
    },

    # set to 1 to output debugging information
    'debug': 0,

    # Signing
    'key_file': '/home/django/certs/faraday.key',  # private part
    'cert_file': '/home/django/certs/faraday_ele_tue_nl.crt',  # public part
    # Encryption
    'encryption_keypairs': [{
        'key_file': '/home/django/certs/faraday.key',  # private part
        'cert_file': '/home/django/certs/faraday_ele_tue_nl.crt',  # public part
    }],

    # own metadata settings
    'contact_person': [
        {'given_name': 'Frank',
         'sur_name': 'Boerman',
         'company': 'Kolibri Solutions',
         'email_address': DEV_EMAIL,
         'contact_type': 'technical'},
        {'given_name': 'Sjoerd',
         'sur_name': 'Hulshof',
         'company': 'TU/e ELE',
         'email_address': CONTACT_EMAIL,
         'contact_type': 'administrative'},
    ],
    'valid_for': 24,  # how long is our metadata valid, needs to be short because letsencrypt certs
}

SAML_DJANGO_USER_MAIN_ATTRIBUTE = 'email' # Use email to match saml users to django users
SAML_DJANGO_USER_MAIN_ATTRIBUTE_LOOKUP = '__iexact'
SAML_CREATE_UNKOWN_USER = True
SAML_USE_NAME_ID_AS_USERNAME = False
SAML_LOGOUT_REQUEST_PREFERRED_BINDING = saml2.BINDING_HTTP_REDIRECT
# all other mappings (the less simple ones) are done in djangosaml2_custom/signals/handler.py
SAML_ATTRIBUTE_MAPPING = {
    'urn:mace:dir:attribute-def:uid': ('username', ),
    'urn:mace:dir:attribute-def:mail': ('email', ),
}
SAML_ACS_FAILURE_RESPONSE_FUNCTION = 'djangosaml2_custom.acs_failures.template_failure'
