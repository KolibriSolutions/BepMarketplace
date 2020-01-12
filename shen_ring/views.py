#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import base64
import json

import requests
from django.conf import settings
from django.contrib import auth
from django.core import serializers
from django.core import signing
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.middleware import csrf
from django.shortcuts import render
from django.utils.http import is_safe_url
from django.views.decorators.csrf import ensure_csrf_cookie
from oauthlib.oauth2 import WebApplicationClient, MissingCodeError

from BepMarketplace.utils import get_user
from general_view import get_grouptype
from osirisdata.data import osirisData
from osirisdata.models import AccessGrant
from timeline.utils import get_timephase_number, get_timeslot

import logging

logger = logging.getLogger('django')


def set_level(user):
    try:
        grant = AccessGrant.objects.get(Email=user.email)
    except AccessGrant.DoesNotExist:
        return

    if grant.Level == 1:
        user.groups.add(get_grouptype("1"))
        user.save()
    if grant.Level == 2:
        if get_grouptype("2u") in user.groups.all():
            user.groups.remove(get_grouptype("2u"))
        user.groups.add(get_grouptype("2"))
        user.save()


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
        meta.ECTS = osirisdata.ects
        meta.Studentnumber = osirisdata.idnumber
        meta.full_clean()
        meta.save()


def is_staff(user):
    """
    Check whether the user is staff. Staff has an @tue.nl email, students have @student.tue.nl email.

    :param user:
    :return:
    """
    if user.email.split('@')[-1].lower() in settings.STAFF_EMAIL_DOMAINS or get_grouptype('3') in user.groups.all():
        return True
    return False


def enrolled_osiris(user):
    """
    Check whether the user is enrolled in Osiris for the BEP course

    :param user:
    :return:
    """
    try:
        meta = user.usermeta
    except:
        return False
    return meta.EnrolledBEP


def check_user(request, user):
    # insert checks on login here
    if user.is_superuser:
        return render(request, 'base.html', status=403, context={
            'Message': 'Superusers are not allowed to login via SSO. Please use 2FA login.'})
    else:
        # block all except supportstaff if there is no timeslot
        # support staff needs login to be able to set a new timeslot or timephase.
        if not get_timeslot() and not get_grouptype('3') in user.groups.all():  # if there isn't a timeslot and not type3
            return render(request, 'base.html', status=403, context={"Message": "Login is currently not available."})

        # login functions for staff and students.
        if is_staff(user):
            set_level(user)
            if not user.groups.exists():
                # existing staff member already have groups
                # new staff members get automatically type2staffunverified
                user.groups.add(get_grouptype("2u"))
            return True
        else:
            if not enrolled_osiris(user):
                return render(request, 'base.html', status=403, context={"Message": "You are not enrolled in our system yet. Please login once through canvas module BEP Marketplace"})
            elif get_timephase_number() < 3:  # if there isn't a timephase, this returns -1, so login is blocked.
                return render(request, 'base.html', status=403, context={"Message": "Student login is not available in "
                                                                                    "this timephase."})
            else:
                # student is enrolled in osiris. Set its usermeta from the osiris data
                data = osirisData()
                osirisdata = data.get(user.email)
                if osirisdata is not None:
                    set_osiris(user, osirisdata)

                if get_timephase_number() > 5:  # only students with project are allowed
                    if not user.distributions.exists():
                        return render(request, 'base.html', status=403,
                                      context={"Message": "You don't have a project assigned"
                                                          " to you, therefore login is not "
                                                          "allowed in this timephase."})

                if get_timeslot() not in user.usermeta.TimeSlot.all():  # user is not active in this timeslot
                    # not in this timeslot so old user, canvas app sets timeslot
                    # this security will fail if canvas does not close off old courses as it does now
                    return render(request, 'base.html', status=403, context={"Message": "You already did your BEP once"
                                                                                        ", login is not allowed."})
    return True


def callback(request):
    # parse the incoming answer from oauth
    client = WebApplicationClient(settings.SHEN_RING_CLIENT_ID)
    try:
        response = client.parse_request_uri_response(request.build_absolute_uri())
    except MissingCodeError:
        if 'error' in request.GET:
            raise PermissionDenied(request.GET.get('error'))
        else:
            raise PermissionDenied("Authentication failed")

    if not settings.SHEN_RING_NO_CSRF:
        if 'state' not in response:
            raise PermissionDenied("Authentication failed. (csrf state not available)")

        if '-' in response['state']:
            csrf_token, next_url = response['state'].split('-')
            next_url = base64.b64decode(next_url.encode()).decode()
        else:
            csrf_token = response['state']
            next_url = None

        if request.session.get(csrf.CSRF_SESSION_KEY, '') != csrf_token:
            raise PermissionDenied("Authentication failed. (csrf token failed)")
    else:
        if '-' in response.get('state', ""):
            next_url = base64.b64decode(response['state'].strip('-').encode()).decode()
        else:
            next_url = None

    # upgrade grant code to access code
    session = requests.Session()
    session.headers['User-Agent'] = settings.NAME_PRETTY
    # get parameters
    data = client.prepare_request_body(code=response['code'], client_secret=settings.SHEN_RING_CLIENT_SECRET,
                                       include_client_id=True)
    # convert to requests dictionary
    data_dict = {}
    for itm in data.split("&"):
        data_dict[itm.split('=')[0]] = itm.split('=')[1]

    # request accesstoken
    try:
        access_code_data = requests.post(settings.SHEN_RING_URL + "oauth/token/", data=data_dict).json()
    except:
        raise PermissionDenied("Authentication failed. (invalid_json_data)")
    if 'access_token' not in access_code_data:
        raise PermissionDenied(access_code_data['error'])

    # request account information
    # this assumes that timeslot pk is identical on both shen and local db!
    r = session.get(settings.SHEN_RING_URL + "info/", headers={"Authorization": "Bearer {}".format(access_code_data["access_token"])})

    if r.status_code != 200:
        raise PermissionDenied("Authentication failed. (shen_link_failed)")

    try:
        value = json.dumps(signing.loads(r.text, settings.SHEN_RING_CLIENT_SECRET))
    except signing.BadSignature:
        raise PermissionDenied("Authentication failed. (shen_signing_failed)")

    # login or create the user
    try:
        user, usermeta = serializers.deserialize('json', value)
    except:
        raise PermissionDenied('Authentication failed. (corrupted_user_info_retrieved)')
    # data from info is directly saved to db, this means that the appointed shen system is fully trusted
    #  this is breached when the shen server is man in the middled, but then an attacker needs to steal both the domain as well as the secret keys

    # find user and map shen user to local user
    existent_user = get_user(user.object.email, user.object.username)
    if existent_user:
        if not existent_user.is_active:
            raise PermissionDenied("Your user is disabled. Please contact support.")
        user.object.pk = existent_user.pk
        existent_usermeta = existent_user.usermeta
        usermeta.object.pk = existent_usermeta.pk
        groups = list(existent_user.groups.all())
        timeslots = list(existent_usermeta.TimeSlot.all())

        # for fields that do not exist on shen but do exist on local, port the value over otherwise data is lost
        for local_field in settings.USERMETA_LOCAL_FIELDS:
            setattr(usermeta.object, local_field, getattr(existent_usermeta, local_field))
        try:
            user.save()
            usermeta.object.User = user.object
            usermeta.save()
        except Exception as e:
            logger.exception('User save failed with Shen login for existing user {}. Exception {}'.format(user, e))
            raise PermissionDenied("Something went wrong while logging you in. Please contact support at {} to get this resolved.".format(settings.CONTACT_EMAIL))
        # overwrite the timeslots, this needs to be done after usermeta save due to begin a m2m relation
        usermeta.object.TimeSlot.clear()
        for ts in timeslots:
            usermeta.object.TimeSlot.add(ts)
        usermeta.object.save()
        # foreignkeys on the user to other models are wiped with this method, foreignkeys from other models to user keep working
        # has to be done after save because its an m2m relation
        for group in groups:
            user.object.groups.add(group)
        user.object.save()
    elif existent_user is None:
        # user does not exist
        user.object.pk = None
        usermeta.object.pk = None
        try:
            user.save()
            usermeta.object.User = user.object
            usermeta.save()
            # clear timeslots as this is handled internally
            usermeta.object.TimeSlot.clear()
            usermeta.save()
        except Exception as e:
            logger.exception('User save failed with Shen login for new user {}. Exception {}'.format(user, e))
            raise PermissionDenied("Something went wrong while logging you in. Please contact support at {} to get this resolved.".format(settings.CONTACT_EMAIL))
    else:
        # more then one user found with this combination, db corrupted, abort
        # this will not happen, as get_user already raises exception
        return HttpResponseNotFound()
    user = user.object
    usermeta = usermeta.object
    response = check_user(request, user)
    if response is not True:
        return response

    # login user
    auth.login(request, user)

    if next_url is not None:
        if is_safe_url(next_url, None):
            return HttpResponseRedirect(next_url)

    return HttpResponseRedirect("/")


@ensure_csrf_cookie
def login(request):
    """
    Set session cookie and redirect to shen
    :param request:
    :return:
    """
    client = WebApplicationClient(settings.SHEN_RING_CLIENT_ID)
    if not settings.SHEN_RING_NO_CSRF:
        state = request.META.get("CSRF_COOKIE", "ERROR")
    else:
        state = ""
    if request.GET.get('next', None) is not None:
        state += "-" + base64.b64encode(request.GET.get('next').encode()).decode()
    url = client.prepare_request_uri(settings.SHEN_RING_URL + "oauth/authorize/", state=state, approval_prompt='auto')
    return HttpResponseRedirect(url)
