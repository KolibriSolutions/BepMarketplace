import json
import logging
import time

import channels
from django.conf import settings
from django.contrib import auth
from django.core.exceptions import SuspiciousOperation
from django.http import HttpResponseRedirect  # 30x
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from djangosaml2.cache import IdentityCache, OutstandingQueriesCache
from djangosaml2.conf import get_config
from djangosaml2.overrides import Saml2Client
from djangosaml2.signals import post_authenticated
from djangosaml2.utils import get_custom_setting, fail_acs_response
from djangosaml2.views import _set_subject_id
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from saml2.response import StatusAuthnFailed, SignatureError, StatusRequestDenied, UnsolicitedResponse
from saml2.response import StatusError
from saml2.sigver import MissingKey
from saml2.validate import ResponseLifetimeExceed, ToEarly

from general_view import get_grouptype
from timeline.utils import get_timephase_number, get_timeslot
from osirisdata.data import osirisData
from tracking.models import UserLogin

from djangosaml2_custom.acs_failures import unsolicited_response

from datetime import datetime
from pytz import utc
from ipware.ip import get_real_ip

logger = logging.getLogger('djangosaml2')

def set_osiris(user, osirisdata):
    """
    Set usermeta based on osiris data

    :param user:
    :param osirisdata:
    :return:
    """
    meta = user.usermeta
    if not meta.Overruled:
        if osirisdata.automotive:
            meta.Study = 'Automotive'
        else:
            meta.Study = 'Eletrical Engineering'
        meta.Cohort = osirisdata.cohort
        meta.EnrolledBEP = osirisdata.enrolled
        meta.EnrolledExt = osirisdata.enrolledextension
        meta.ECTS = osirisdata.ects
        meta.save()

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
    data = osirisData()
    userdata = data.get(user.email)
    if userdata is None:
        return False
    else:
        return userdata.enrolled

def request_info(request):
    """
    Extra info from a request to give to logging

    :param request:
    :return:
    """
    return '; ip: '+ get_real_ip(request) + \
           '; timestamp: ' + str(datetime.utcnow()) +\
           '; user_agent: ' + request.META.get('HTTP_USER_AGENT')


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

    This view is called instead of djangosaml2/views because of overriden urls.py
    """
    attribute_mapping = attribute_mapping or get_custom_setting('SAML_ATTRIBUTE_MAPPING', {'uid': ('username', )})
    create_unknown_user = create_unknown_user if create_unknown_user is not None else \
                          get_custom_setting('SAML_CREATE_UNKNOWN_USER', True)
    conf = get_config(config_loader_path, request)
    try:
        xmlstr = request.POST['SAMLResponse']
    except KeyError:
        logger.warning('Missing "SAMLResponse" parameter in POST data.'+request_info(request))
        raise SuspiciousOperation

    client = Saml2Client(conf, identity_cache=IdentityCache(request.session))

    oq_cache = OutstandingQueriesCache(request.session)
    outstanding_queries = oq_cache.outstanding_queries()

    try:
        response = client.parse_authn_request_response(xmlstr, BINDING_HTTP_POST, outstanding_queries)
    except (StatusError, ToEarly):
        logger.exception("Error processing SAML Assertion."+request_info(request))
        return fail_acs_response(request)
    except ResponseLifetimeExceed:
        logger.info("SAML Assertion is no longer valid. Possibly caused by network delay or replay attack."+request_info(request), exc_info=True)
        return fail_acs_response(request)
    except SignatureError:
        logger.info("Invalid or malformed SAML Assertion."+request_info(request), exc_info=True)
        return fail_acs_response(request)
    except StatusAuthnFailed:
        logger.info("Authentication denied for user by IdP."+request_info(request), exc_info=True)
        return fail_acs_response(request)
    except StatusRequestDenied:
        logger.warning("Authentication interrupted at IdP."+request_info(request), exc_info=True)
        return fail_acs_response(request)
    except MissingKey:
        logger.exception("SAML Identity Provider is not configured correctly: certificate key is missing!"+request_info(request))
        return fail_acs_response(request)
    except UnsolicitedResponse:
        # use a warning to stop stupid email notifications
        logger.warning("Received SAMLResponse when no request has been made. (Unsolicited response)"+request_info(request), exc_info=True)
        # return fail_acs_response(request)
        # special message because this is a very common error.
        return unsolicited_response(request)
    except:
        logger.exception("Djangosaml2 final exception. This should not happen!"+request_info(request), exc_info=True)
        return fail_acs_response(request, status=400, exc_class=SuspiciousOperation)

    if response is None:
        logger.warning("Invalid SAML Assertion received (unknown error)."+request_info(request))
        return fail_acs_response(request, status=400, exc_class=SuspiciousOperation)

    session_id = response.session_id()
    oq_cache.delete(session_id)

    # authenticate the remote user
    session_info = response.session_info()

    if callable(attribute_mapping):
        attribute_mapping = attribute_mapping()
    if callable(create_unknown_user):
        create_unknown_user = create_unknown_user()

    logger.debug('Trying to authenticate the user. Session info: %s', session_info)
    user = auth.authenticate(request=request,
                             session_info=session_info,
                             attribute_mapping=attribute_mapping,
                             create_unknown_user=create_unknown_user)
    if user is None:
        logger.warning("Could not authenticate user received in SAML Assertion. Session info: %s", session_info)
        return render(request, 'base.html', status=403, context=
            {"Message": "You are not allowed to log in. Your user account might be disabled. Please contact the "
                        "support staff at " + settings.CONTACT_EMAIL})

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
            data = osirisData()
            osirisdata = data.get(user.email) #enrollment is already checked so this always returns a person object
            set_osiris(user, osirisdata)

            if get_timephase_number() > 5:  # only students with project are allowed
                if not user.distributions.exists():
                    return render(request, 'base.html', status=403, context={"Message":"You don't have a project assigned"
                                                                                   " to you, therefore login is not "
                                                                                   "allowed in this timephase."})

            if get_timeslot() not in user.usermeta.TimeSlot.all():  # user is not active in this timeslot
                # since enrollment was already checked so make this student active in this timeslot
                user.usermeta.TimeSlot.add(get_timeslot())
                # if not user.usermeta.TimeSlot.exists():    # user has no timeslot, add the current timeslot
                #     # user has no timeslot
                #     user.usermeta.TimeSlot.add(get_timeslot())
                # else:  # user was active in another timeslot
                #     return render(request, 'base.html', status=403, context={"Message": "You already did your BEP once"
                #                                                                     ", login is not allowed."})

    auth.login(request, user)
    _set_subject_id(request.session, session_info['name_id'])
    logger.debug("User %s authenticated via SSO.", user)

    #TODO, this signal is not send correctly: https://github.com/knaperek/djangosaml2/issues/117
    logger.debug('Sending the post_authenticated signal')
    post_authenticated.send_robust(sender=user, session_info=session_info)

    #TODO after signal is send correctly, move all loging to the signal function in handlers.py
    # log the login
    log = UserLogin()
    log.Subject = user
    log.save()


    # redirect the user to the view where he came from
    default_relay_state = get_custom_setting('ACS_DEFAULT_REDIRECT_URL',
                                             settings.LOGIN_REDIRECT_URL)
    relay_state = request.POST.get('RelayState', default_relay_state)
    if not relay_state:
        logger.warning('The RelayState parameter exists but is empty')
        relay_state = default_relay_state
    if not is_safe_url(url=relay_state, host=request.get_host()):
        relay_state = settings.LOGIN_REDIRECT_URL
    logger.debug('Redirecting to the RelayState: %s', relay_state)
    return HttpResponseRedirect(relay_state)