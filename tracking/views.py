import json
from datetime import datetime

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import User
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.shortcuts import render

from BepMarketplace.decorators import superuser_required
from general_view import get_sessions
from timeline.utils import get_timeslot
from .models import ProposalStatusChange, UserLogin, ProposalTracking, ApplicationTracking


def getTrack(proposal):
    """
    try retrieving the object from cache, if not in cache from db, if not in db, create it. update cache accordingly

    :param proposal:
    :return:
    """
    ctrack = cache.get('trackprop{}'.format(proposal.id))
    if ctrack is None:
        try:
            track = ProposalTracking.objects.get(Subject=proposal)
        except ProposalTracking.DoesNotExist:
            track = ProposalTracking()
            track.Subject = proposal
            track.save()
        cache.set('trackprop{}'.format(proposal.id), track, None)
        return track
    else:
        return ctrack


@superuser_required()
def listUserLog(request):
    """
    Shows the list of loginattempts by time.

    :param request:
    :return:
    """
    return render(request, "tracking/listUserLog.html", {
        "userlogs": list(UserLogin.objects.filter(Timestamp__gte=get_timeslot().Begin)),
    })


@superuser_required()
def viewTrackingStatusList(request):
    """
    List of proposal status changes.

    :param request:
    :return:
    """
    return render(request, "tracking/listTrackingStatus.html", {
        "trackings": ProposalStatusChange.objects.filter(Subject__TimeSlot=get_timeslot()).order_by('-Timestamp')
    })


@superuser_required()
def viewTrackingApplicationList(request):
    """
    List of application-apply and application-retracts of all students.

    :param request:
    :return:
    """
    return render(request, "tracking/listTrackingApplication.html", {
        'trackinglist': ApplicationTracking.objects.filter(Proposal__TimeSlot=get_timeslot()).order_by('-Timestamp')
    })


@superuser_required()
def liveStreamer(request):
    """
    Show the livestreamer. This pages shows events like a user logging in. Using websockets.

    :param request:
    :return:
    """
    return render(request, "tracking/liveStreamer.html")


@superuser_required()
def userDetail(request, pk):
    user = get_object_or_404(User, pk=pk)

    try:
        with open('telemetry_cli/data/{}.log'.format(user.username), 'r') as stream:
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


def trackProposalVisit(project, user):
    """
    Add a proposal-visit to the list of visitors to count unique student views to a proposal

    :param project: the proposal
    :param user: the visiting user.
    :return:
    """
    # only for students
    if user.groups.exists() or user.is_superuser:
        return

    # only for published
    if project.Status != 4:
        return

    # retrieve object
    track = getTrack(project)

    # add if it is unique visitor and write to both db and cache
    if user not in track.UniqueVisitors.all():
        track.UniqueVisitors.add(user)
        track.save()
        cache.set('trackprop{}'.format(project.id), track, None)

        # notify listeners
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('viewnumber{}'.format(project.id), {
            'type': 'update',
            'text': str(track.UniqueVisitors.count()),
        })
