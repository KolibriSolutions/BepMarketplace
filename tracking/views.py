#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
import json
from datetime import datetime

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from index.decorators import superuser_required
from general_view import get_sessions
from timeline.utils import get_timeslot
from .models import ProposalStatusChange, UserLogin, ApplicationTracking
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import zipfile
from io import BytesIO
from django.http import HttpResponse
from django.core.exceptions import PermissionDenied
from .models import TelemetryKey
import os
from django.conf import settings

@superuser_required()
def list_user_login(request):
    """
    Shows the list of loginattempts by time.

    :param request:
    :return:
    """
    return render(request, "tracking/listUserLog.html", {
        "userlogs": list(UserLogin.objects.filter(Timestamp__gte=get_timeslot().Begin)),
    })


@superuser_required()
def list_project_status_change(request):
    """
    List of proposal status changes.

    :param request:
    :return:
    """
    return render(request, "tracking/listTrackingStatus.html", {
        "trackings": ProposalStatusChange.objects.filter(Subject__TimeSlot=get_timeslot()).order_by('-Timestamp')
    })


@superuser_required()
def list_application_change(request):
    """
    List of application-apply and application-retracts of all students.

    :param request:
    :return:
    """
    return render(request, "tracking/listTrackingApplication.html", {
        'trackinglist': ApplicationTracking.objects.filter(Proposal__TimeSlot=get_timeslot()).order_by('-Timestamp')
    })


@superuser_required()
def telemetry_user_detail(request, pk):
    user = get_object_or_404(User, pk=pk)

    try:
        with open('tracking/telemetry/data/{}.log'.format(user.username), 'r') as stream:
            telemetry = json.loads('[{}]'.format(','.join(stream.readlines())).replace('\n', ''))
    except:
        telemetry = []

    pages_count = {}

    for line in telemetry:
        line['timestamp'] = datetime.fromtimestamp(line['timestamp'])
        try:
            pages_count[line['path']] += 1
        except:
            pages_count[line['path']] = 1

    return render(request, 'tracking/userTrackingDetail.html', {
        'session': len(get_sessions(user)) != 0,
        'target': user,
        'telemetry': telemetry,
        'toppages': sorted(pages_count, key=pages_count.__getitem__, reverse=True)[:3],
    })

@csrf_exempt
@require_http_methods(['POST'])
def download_telemetry(request):
    key = request.POST.get('key', None)
    if key is None:
        raise PermissionDenied("No key specified")
    try:
        key_obj = TelemetryKey.objects.get(key=key)
        if not key_obj.is_valid():
            raise PermissionDenied("Key not valid")
    except TelemetryKey.DoesNotExist:
        raise PermissionDenied("Key not valid")


    in_memory = BytesIO()
    zipf = zipfile.ZipFile(in_memory, 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(os.path.join(settings.BASE_DIR, "tracking/telemetry/data/")):
        for file in files:
            zipf.write(os.path.join(root, file), arcname="logs/" + file)

    zipf.close()


    response = HttpResponse(content_type="application/zip")
    response['Content-Disposition'] = 'attachment; filename="logs.zip"'

    in_memory.seek(0)
    response.write(in_memory.read())

    return response
