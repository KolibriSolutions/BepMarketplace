#  Bep Marketplace ELE
#  Copyright (c) 2016-2022 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import redirect
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
    try:
        username = data['lis_person_sourcedid']
        email = data['lis_person_contact_email_primary']
        studentnumber = data['custom_canvas_user_login_id']
        coursecode = data['context_label']
    except KeyError as e:
        logger.error('Invalid post data from canvas; {}; {}'.format(data, e))
        return HttpResponse("Missing data in POST", status=400)

    user = get_user(email, username)
    if user is None:
        user = User(email=email, username=username)
        user.save()
    try:
        meta = user.usermeta
    except UserMeta.DoesNotExist:
        meta = UserMeta(User=user)

    meta.Studentnumber = studentnumber
    if not meta.Overruled:
        if settings.COURSE_CODE_BEP in coursecode:
            meta.EnrolledBEP = True
        elif settings.COURSE_CODE_EXT in coursecode:
            meta.EnrolledBEP = True
            meta.EnrolledExt = True
        else:
            logger.warning('Course code not matched on BEP or EXT for user {}. Code was: {}'.format(user, coursecode))

    meta.save()
    meta.TimeSlot.add(get_timeslot())
    meta.save()
    user.save()

    log = CanvasLogin()
    log.Subject = user
    log.save()

    return redirect("{}/login/".format(settings.DOMAIN))
