from oauthlib.oauth2 import WebApplicationClient,  MissingCodeError
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponseNotFound
import requests
from django.core import serializers
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib import auth
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from general_view import get_grouptype
from osirisdata.data import osirisData
from timeline.utils import get_timephase_number, get_timeslot
from django.middleware import csrf
from django.core import signing
import json
from osirisdata.models import AccessGrant

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
    #parse the incomming answer from oauth
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
            raise PermissionDenied("csrf_state_check_failed")

        if request.session.get(csrf.CSRF_SESSION_KEY, '') != response['state']:
            raise PermissionDenied("csrf_state_check_failed")

    #upgrade grant code to access code
    session = requests.Session()
    session.headers['User-Agent'] = 'BEP Marketplace ELE'
    #get parameters
    data = client.prepare_request_body(code=response['code'], client_secret=settings.SHEN_RING_CLIENT_SECRET,
                                include_client_id=True)
    # convert to requests dictionary
    data_dict = {}
    for itm in data.split("&"):
        data_dict[itm.split('=')[0]] = itm.split('=')[1]

    #request accesstoken
    try:
        access_code_data = requests.post(settings.SHEN_RING_URL + "oauth/token/", data=data_dict).json()
    except:
        raise PermissionDenied("invalid_json_data")
    if 'access_token' not in access_code_data:
        raise PermissionDenied(access_code_data['error'])

    #request account information
    ## this assumes that timeslot pk is identical on both shen and local db!
    r = session.get(settings.SHEN_RING_URL + "info/", headers={"Authorization" : "Bearer {}".format(access_code_data["access_token"])})

    if r.status_code != 200:
        raise PermissionDenied("shen_link_failed")

    try:
        value = json.dumps(signing.loads(r.text, settings.SHEN_RING_CLIENT_SECRET))
    except signing.BadSignature:
        raise PermissionDenied("shen_signing_failed")


    #login or create the user
    try:
        user, usermeta = serializers.deserialize('json', value)
    except:
        raise PermissionDenied('corrupted_user_info_retrieved')
    ## data from info is directly saved to db, this means that the appointed shen system is fully trusted
    ##  this is breached when the shen server is man in the middled, but then an attacker needs to steal both the domain as well as the secret keys


    if User.objects.filter(Q(username=user.object.username) & Q(email=user.object.email)).count() == 1:
        #user exists
        existent_user = User.objects.filter(Q(username=user.object.username) & Q(email=user.object.email))[0]
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
        except:
            raise PermissionDenied("Authentication failed")
        #overwrite the timeslots, this needs to be done after usermeta save due to begin a m2m relation
        usermeta.object.TimeSlot.clear()
        for ts in timeslots:
            usermeta.object.TimeSlot.add(ts)
        usermeta.object.save()
        #foreignkeys on the user to other models are wiped with this method, foreignkeys from other models to user keep working
        # has to be done after save because its an m2m relation
        for group in groups:
            user.object.groups.add(group)
        user.object.save()
    elif User.objects.filter(Q(username=user.object.username) & Q(email=user.object.email)).count() == 0:
        #user does not exist
        user.object.pk = None
        usermeta.object.pk = None
        try:
            user.save()
            usermeta.object.User = user.object
            usermeta.save()
            # clear timeslots as this is handled internally
            usermeta.object.TimeSlot.clear()
            usermeta.save()
        except:
            raise PermissionDenied("Authentication failed")
    else:
        #more then one user found with this combination, db corrupted, abort
        return HttpResponseNotFound()
    user = user.object
    usermeta = usermeta.object
    response = check_user(request, user)
    if response is not True:
        return response

    #login user
    auth.login(request, user)

    #TODO: fix that next parameter is taken into account
    return HttpResponseRedirect("/")



def login(request):
    client = WebApplicationClient(settings.SHEN_RING_CLIENT_ID)
    if not settings.SHEN_RING_NO_CSRF:
        csrftoken = request.session.get(csrf.CSRF_SESSION_KEY, "")
        if csrftoken == "":
            csrftoken = csrf.get_token(request)
            request.session[csrf.CSRF_SESSION_KEY] = csrftoken
        url = client.prepare_request_uri(settings.SHEN_RING_URL + "oauth/authorize/", state=csrftoken, approval_prompt='auto')
    else:
        url = client.prepare_request_uri(settings.SHEN_RING_URL + "oauth/authorize/", approval_prompt='auto')
    return HttpResponseRedirect(url)