#  Bep Marketplace ELE
#  Copyright (c) 2016-2020 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from importlib import import_module

from django.conf import settings
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Count
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.utils import timezone

from index.decorators import superuser_required
from general_view import get_grouptype, get_all_students
from timeline.utils import get_timeslot
from tracking.models import ProposalTracking
from tracking.models import UserLogin


@superuser_required()
def getVisitors(request, pk):
    """
    Raw HTML output of visitors of given proposal. Used for the popup menu on visitorsProposalOverview.

    :param request:
    :param pk:
    :return:
    """
    obj = get_object_or_404(ProposalTracking, pk=pk)
    return render(request, 'godpowers/visitorslist.html', {'track': obj})


@superuser_required()
def visitorsProposalOverview(request):
    """
    Lists all proposals with a button to view its visitors and a count of the number of unique visitors.

    :param request:
    :return:
    """
    props = ProposalTracking.objects.filter(Subject__TimeSlot=get_timeslot()).annotate(
        q_count=Count('UniqueVisitors')).order_by('-q_count')

    return render(request, 'godpowers/visitorsoverview.html', {
        'props': props,
    })


@superuser_required()
def visitorOverview(request, pk):
    """
    List of all proposals visited by a given user.

    :param request:
    :param pk:
    :return:
    """
    usr = get_object_or_404(User, pk=pk)
    props = [trk.Subject for trk in ProposalTracking.objects.filter(UniqueVisitors=usr)]

    return render(request, 'proposals/list_projects.html', {'proposals': props, 'usrsubject': usr})


@superuser_required()
def visitorsMenu(request):
    """
    List of all students, click on the student to view the proposals that he/she visited.

    :param request:
    :return:
    """

    return render(request, 'godpowers/visitorsmenu.html', {'students': get_all_students()})


@superuser_required()
def clearCache(request):
    """
    Clear the full REDIS cache

    :param request:
    :return:
    """
    cache.clear()
    return render(request, "base.html", {"Message": "Cache cleared!"})


@superuser_required()
def sessionList(request):
    """
    List all active sessions (logged in users) with the possibility to kill a session (logout the user)

    :param request:
    """
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    uid_list = []

    for session in sessions:
        data = session.get_decoded()
        uid_list.append(data.get('_auth_user_id', None))
    users = []

    for user in User.objects.filter(id__in=uid_list):
        if get_grouptype("3") in user.groups.all():
            continue
        try:
            lastlogin = UserLogin.objects.filter(Subject=user).latest('Timestamp')
            users.append({'user': user, 'lastlogin': lastlogin})
        except:  # a session without a user (should not happen, only when user is deleted recently)
            pass

    return render(request, "godpowers/listSessions.html", {"users": users})


def init_session(session_key):
    """
    Helper function to kill a session

    :param session_key:
    :return:
    """
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key)


@superuser_required()
def killSession(request, pk):
    """
    Kill a session of a user. Usually called from the sessionList page.

    :param request:
    :param pk: id of the user to kill session for
    """
    for session in Session.objects.all():
        if session.get_decoded().get('_auth_user_id', None) == pk:
            request = HttpRequest()
            request.session = init_session(session.session_key)
            auth_logout(request)
    return render(request, "base.html", {"Message": "User logged out", "return": "godpowers:sessionlist"})
