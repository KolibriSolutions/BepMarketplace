import json
import time

import channels
from django.conf import settings
from django.contrib import auth
from django.http import HttpResponseRedirect  # 30x
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djangosaml2.cache import IdentityCache, OutstandingQueriesCache
from djangosaml2.conf import get_config
from djangosaml2.signals import post_authenticated
from djangosaml2.utils import get_custom_setting
from djangosaml2.views import _set_subject_id
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.response import StatusError
from saml2.sigver import MissingKey

from general_view import get_timephase_number, get_grouptype, get_timeslot
from index.models import UserMeta
from tracking.models import UserLogin


def set_attributes(user, attributes):
    """
    Set the SAML attributes of the user. Stored in user and in usermeta. 
    
    :param user: 
    :param attributes: 
    :return: 
    """
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta()

    # make last name from fullname
    meta.Fullname = attributes["urn:mace:dir:attribute-def:displayName"][0]
    user.email = attributes["urn:mace:dir:attribute-def:mail"][0].lower()

    # these attributes don't always exist
    try:
        meta.Initials = attributes["Initials"][0]
        user.last_name = attributes["urn:mace:dir:attribute-def:sn"][0]
        user.first_name = attributes["urn:mace:dir:attribute-def:givenName"][0].split(' ')[0]  # take first if multiple.
    except:
        user.last_name = meta.Fullname

    user.save()
    user.usermeta = meta
    user.save()
    meta.save()


def set_osiris(user, osirisdata):
    """
    Set usermeta based on osiris data
    
    :param user: 
    :param osirisdata: 
    :return: 
    """
    meta = user.usermeta
    if not meta.Overruled:
        pass
        # From Osiris:
        #meta.Department = ldapobj['data']['department']
        #meta.Study = ldapobj['data']['study']
        #meta.Cohort = ldapobj['data']['cohort']
        #meta.Studentnumber = ldapobj['data']['studentnumber']
        #meta.Culture = ldapobj['data']['culture']
        #meta.EnrolledBEP = ldapobj['data']['enrolledBEP']
        #meta.EnrolledExt = ldapobj['data']['enrolledExt']

def is_staff(user):
    """
    Check whether the user is staff. Staff has an @tue.nl email, students have @student.tue.nl email.
    
    :param user: 
    :return: 
    """
    if user.email[-7:] == "@tue.nl":
        return True
    return False


def enrolled_osiris(user):
    """
    Check whether the user is enrolled in Osiris for the BEP course
    
    :param user: 
    :return: 
    """
    return True


@require_POST
@csrf_exempt
def assertion_consumer_service(request,
                               config_loader_path=None,
                               attribute_mapping=None,
                               create_unknown_user=None):
    """SAML Authorization Response endpoint

    The IdP will send its response to this view, which
    will process it with pysaml2 help and log the user
    in using the custom Authorization backend
    djangosaml2.backends.Saml2Backend that should be
    enabled in the settings.py
    After successfull login, it redirects the user to the RelayState parameter of the SAML response. This is either 
    the homepage or a page supplied with the ?next= value when it was a redirected login. 
    
    This is a custom version derived from the assertion_consumer_service from djangosaml2.views.
    It also checks OSIRIS subscription, or adds groups for staff members. Next it fills the usermeta for users.
    It does not use the attribute_mapping from settings.py
    """

    # Attribute mapping is not used, but a default needs to be set for the backend to work.
    attribute_mapping = attribute_mapping or get_custom_setting(
            'SAML_ATTRIBUTE_MAPPING', {'uid': ('username', )})

    create_unknown_user = True

    conf = get_config(config_loader_path, request)
    if 'SAMLResponse' not in request.POST:
        return render(request, 'base.html', status=400, context=
            {"Message": 'Login failed, bad request. (Couldn\'t find "SAMLResponse" in POST data.)'})
    xmlstr = request.POST['SAMLResponse']
    client = Saml2Client(conf, identity_cache=IdentityCache(request.session))

    oq_cache = OutstandingQueriesCache(request.session)
    outstanding_queries = oq_cache.outstanding_queries()

    try:
        response = client.parse_authn_request_response(xmlstr, BINDING_HTTP_POST,
                                                       outstanding_queries)
    except StatusError:
        return render(request, 'base.html', status=403, context=
            {"Message": "Something went wrong while logging you in. (Authentication error)"})

    except MissingKey:
        return render(request, 'base.html', status=403, context=
            {"Message": "Something went wrong while logging you in. (The Identity Provider is not configured correctly:"
                " the certificate key is missing)"})
    except:
        return render(request, 'base.html', status=403, context=
            {"Message": "Something went wrong while logging you in. Please try again using the login button."
                        " If that doesn't work, contact support staff. (Other error / Unsolicited response)"})

    if response is None:
        return render(request, 'base.html', status=400, context=
            {"Message": "Something went wrong while logging you in. Bad request. (SAML response has errors."})

    session_id = response.session_id()
    oq_cache.delete(session_id)

    # authenticate the remote user
    session_info = response.session_info()

    # log in using the authentication backend.
    user = auth.authenticate(session_info=session_info,
                             attribute_mapping=attribute_mapping,
                             create_unknown_user=create_unknown_user)
    if user is None:
        return render(request, 'base.html', status=403, context=
            {"Message": "You are not allowed to log in. Your user account might be disabled. Please contact the "
                        "support staff"})

    # set the extra user attributes based on the saml attributes
    attributes = session_info['ava']
    set_attributes(user, attributes)

    # block all except supportstaff if there is no timeslot
    if not get_timeslot() and not get_grouptype('3') in user.groups.all():  # if there isn't a timeslot and not type3
        return render(request, 'base.html', status=403, context={"Message": "Login is currently not available."})

    # login functions for staff and students.
    if is_staff(user):
        if not user.groups.exists():
            # existing staff member already have groups
            # new staff members get automatically type2staffunverified
            user.groups.add(get_grouptype("2u"))
    else:
        # user is a student
        if get_timephase_number() < 3: # if there isn't a timephase, this returns -1, so login is blocked.
            return render(request, 'base.html', status=403, context={"Message": "Student login is not available in "
                                                                                "this timephase."})

        elif not enrolled_osiris(user):
            return render(request, 'base.html', status=403, context={"Message":"You are not yet enrolled in the BEP"
                                                                               "course in Osiris. You are allowed to the "
                                                                           "BEP Marketplace after you enrolled in "
                                                                           "Osiris"})
        else:
            # student is enrolled in osiris. Set its usermeta from the osiris data
            osirisdata = None # to be implemented...
            set_osiris(user, osirisdata)

            if get_timephase_number() > 5:  # only students with project are allowed
                if not user.distributions.exists():
                    return render(request, 'base.html', status=403, context={"Message":"You don't have a project assigned"
                                                                                   " to you, therefore login is not "
                                                                                   "allowed in this timephase."})

            if get_timeslot() not in user.usermeta.TimeSlot.all():  # user is not active in this timeslot
                if not user.usermeta.TimeSlot.exists():    # user has no timeslot, add the current timeslot
                    # user has no timeslot
                    user.usermeta.TimeSlot.add(get_timeslot())
                else:  # user was active in another timeslot
                    return render(request, 'base.html', status=403, context={"Message": "You already did your BEP once"
                                                                                    ", login is not allowed."})

    auth.login(request, user)
    _set_subject_id(request.session, session_info['name_id'])

    # send the signal for post auth
    post_authenticated.send_robust(sender=user, session_info=session_info)

    # log the login
    log = UserLogin()
    log.Subject = user
    if 'next' in request.GET.keys():
        log.Page = request.GET['next']
    log.save()

    # send the login to the livestreamer
    channels.Group('livestream').send({'text': json.dumps({
        'time': time.strftime('%H:%M:%S'),
        'event': 'login',
        'user': str(user),
    })})

    # redirect the user to the view where he came from
    default_relay_state = get_custom_setting('ACS_DEFAULT_REDIRECT_URL',
                                             settings.LOGIN_REDIRECT_URL)

    relay_state = request.POST.get('RelayState', default_relay_state)
    if not relay_state:
        relay_state = default_relay_state
    if not is_safe_url(url=relay_state, host=request.get_host()):
        came_from = settings.LOGIN_REDIRECT_URL
    return HttpResponseRedirect(relay_state)
