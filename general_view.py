"""
General functions that are mostly used in views (views.py).
"""

from datetime import datetime

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from timeline.utils import get_timeslot, get_timephase_number


def get_all_students(undistributed=False):
    """
    Return all active students in marketplace, used for instance for mailing.

    :param undistributed: Also return undistributed students in phase 6 and later.
    :return: user objects
    """

    users = User.objects.filter(
        Q(usermeta__EnrolledBEP=True) & Q(groups=None) & Q(usermeta__TimeSlot=get_timeslot())).distinct()
    if get_timephase_number() < 6 or undistributed:
        return users
    else:
        # only students with a distributions
        return users.filter(Q(distributions__Timeslot=get_timeslot()))


def get_all_staff():
    """
    Get all currently active staff.

    :return:
    """
    return User.objects.filter(groups__isnull=False)


def get_grouptype(shortname):
    """
    Return the Group type2staffunverified object

    :return:
    """
    if shortname == "2u":
        fullname = "type2staffunverified"
    else:
        fullname = "type" + shortname + "staff"

    gt = cache.get("gt" + shortname)
    if gt:
        return gt
    else:
        gt = Group.objects.get(name=fullname)
        cache.set("gt" + shortname, gt, settings.STATIC_OBJECT_CACHE_DURATION)
        return gt


def get_sessions(user):
    sessions = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        if data.get('_auth_user_id', None) == str(user.id):
            sessions.append(session)

    return sessions


def timestamp():
    """
    Timestamp for a xls export

    :return:
    """
    return "{:%Y-%m-%d %H:%M:%S}".format(datetime.now())
