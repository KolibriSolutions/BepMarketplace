from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.shortcuts import redirect
from pylti.common import verify_request_common
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from pylti.common import LTIException
from django.contrib.auth.models import User
from index.models import UserMeta
from timeline.utils import get_timeslot
from tracking.models import CanvasLogin
from BepMarketplace.util import get_user

@require_http_methods(["POST"])
@csrf_exempt
def lti(request):
    config = getattr(settings, 'PYLTI_CONFIG', dict())
    consumers = config.get('consumers', dict())
    params = dict(request.POST.items())
    headers = request.META
    headers['X-Forwarded-Proto'] = headers['HTTP_X_FORWARDED_PROTO']
    try:
        verify_request_common(consumers, request.build_absolute_uri(), request.method, headers, params)
    except LTIException:
        return HttpResponse("Signature Validation failed!", status=403)

    data = request.POST
    try:
        username = data['lis_person_sourcedid']
        email = data['lis_person_contact_email_primary']
        studentnumber = data['custom_canvas_user_login_id']
        coursecode = data['context_label']
    except KeyError:
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
        if coursecode == '5XEC0':
            meta.EnrolledBEP = True
        elif coursecode == '5XED0':
            meta.EnrolledBEP = True
            meta.EnrolledExt = True

    meta.save()
    meta.TimeSlot.add(get_timeslot())
    meta.save()
    user.save()

    log = CanvasLogin()
    log.Subject = user
    log.save()

    return redirect("https://bep.ele.tue.nl/login")
