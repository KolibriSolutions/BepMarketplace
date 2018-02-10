# This module defines a set of useful ACS failure functions that are used to
# produce an output suitable for end user in case of SAML failure.
# customized version of djangosaml2/acs_failures.py
from django.shortcuts import render
from django.conf import settings

def template_failure(request, status=403, **kwargs):
    """Return message that authentication has failed. This is usually because of invalid SAML data."""
    return render(request, 'base.html', status=status, context=
            {"Message": "Something went wrong while logging you in. Please contact the support staff at "
                        + settings.CONTACT_EMAIL + '. '})

def unsolicited_response(request):
    """
    Usually because people press f5 too often on invalid login.
    """
    return render(request, 'base.html', status=403, context=
            {"Message": "Something went wrong while logging you in. "
                        "This can happen when you try to login from another way then using the 'login' button on this website. "
                        "Please try to login using the 'login' button. If the problem persists restart your webbrowser and try again. "
                        "If the problem still persists, contact support staff at "
                        + settings.CONTACT_EMAIL + '. '})
