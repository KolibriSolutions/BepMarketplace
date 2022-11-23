#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import logging

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils.safestring import mark_safe
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from pylti.common import LTIException
from pylti.common import verify_request_common

from BepMarketplace.utils import get_user
from index.models import UserMeta
from timeline.utils import get_timeslot
from tracking.models import CanvasLogin

logger = logging.getLogger('django')


@require_http_methods(["POST"])
@csrf_exempt
def lti(request):
    if not get_timeslot():
        return HttpResponse('Login is not available. The system is currently closed.', status=403)
    config = getattr(settings, 'PYLTI_CONFIG', dict())
    consumers = config.get('consumers', dict())
    params = dict(request.POST.items())
    headers = request.META
    headers['X-Forwarded-Proto'] = 'https'  # super nice way of saying were secure
    try:
        verify_request_common(consumers, request.build_absolute_uri(), request.method, headers, params)
    except LTIException as e:
        logger.error('LTI exception from canvas; {}'.format(e))
        return HttpResponse("Signature Validation failed!", status=403)

    data = request.POST
    assert data['custom_canvas_api_domain'] == 'canvas.tue.nl', 'Error! Invalid CANVAS domain!'

    try:
        username = data['lis_person_sourcedid']
        email = data['lis_person_contact_email_primary']
        studentnumber = data['custom_canvas_user_login_id']
        coursecode = data['context_label']

    except KeyError as e:
        logger.error('Invalid post data from canvas; {}; {}'.format(data, e))
        raise PermissionDenied("Missing CANVAS data in POST. Please contact support")

    ## In case a user is not yet known in the system, make a new user.
    # The new user model and UserMeta is not fully populated, that will be done in the actual login via OIDC/SAML.
    user = get_user(email, username)
    if user is None:
        user = User(email=email, username=username)
        user.save()
    else:  # existing user
        if request.user.is_authenticated:
            if request.user != user:
                logger.error(f"Canvas user {user} tried to login via canvas while {request.user} is already logged in.")
                auth.logout(request)
                raise PermissionDenied("You are already logged in in BepMarketplace using a different user account! You are now logged out.")
        # update existing user:
        if user.email != email:
            logger.warning(f'CANVAS: Email changed for {user} from {user.email} to {email}')
            user.email = email
            user.save()
        if user.username != username:
            logger.warning(f'CANVAS: UID for {user} ({user.username}) is {username}')
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta(User=user)

    if not meta.Overruled:
        meta.Studentnumber = studentnumber
        if settings.COURSE_CODE_BEP in coursecode:
            meta.EnrolledBEP = True
        elif settings.COURSE_CODE_EXT in coursecode:
            meta.EnrolledBEP = True
            meta.EnrolledExt = True
        else:
            logger.error('Course code not matched on BEP or EXT for user {}. Code was: {}'.format(user, coursecode))

    meta.save()
    meta.TimeSlot.add(get_timeslot())

    if not (meta.Fullname or user.last_name or user.first_name):  # only update name if no name is set yet, becaus canvas name is not nice.
        meta.Fullname = data['lis_person_name_full']
        user.last_name = data['lis_person_name_family']
        user.first_name = data['lis_person_name_given']

    log = CanvasLogin()
    log.Subject = user
    log.save()

    try:
        meta.full_clean()
    except ValidationError as e:
        raise Exception(f"Saving updated user {user.email} full_clean failed with {e}")

    meta.save()
    user.save()

    # login
    auth.login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    return render(request, 'base.html', context={'Message':
                                                     mark_safe(
                                                         f'You logged in successfully via CANVAS. From now on, you can also browse the marketplace without CANVAS at <a href="{settings.DOMAIN}/oidc/authenticate/" target="_blank" title="view {settings.HOSTNAME}">{settings.HOSTNAME}</a>'),
                                                 'return': 'index:index'
                                                 }
                  )
    # return redirect('/')
