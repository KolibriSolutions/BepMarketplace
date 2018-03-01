"""
General functions that are mostly used in views (views.py).
"""

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone

from index.models import Track
from students.models import Distribution
from timeline.utils import get_timeslot, get_timephase_number


def get_distributions(user):
    """
    Function to return the distributions that a given staff user is allowed to see
    Type3 and 6 should see all distributions, to be able to mail them.

    :param user: The user to test
    """
    des_all = Distribution.objects.filter(Timeslot=get_timeslot())
    if get_grouptype("3") in user.groups.all() or user.is_superuser or get_grouptype("6") in user.groups.all():
        return des_all
    elif user.tracks.exists():
        tracks = Track.objects.filter(Head=user)
        return des_all.filter(Proposal__Track__in=tracks)
    else:
        return des_all.filter(Q(Proposal__ResponsibleStaff=user) | Q(Proposal__Assistants__id= user.id)).distinct()


def get_all_students(undistributed=False):
    """
    Return all active students in marketplace, used for instance for mailing.

    :param undistributed: Also return undistributed students in phase 6 and later.
    :return: user objects
    """

    users = User.objects.filter(Q(usermeta__EnrolledBEP=True) & Q(groups=None) & Q(usermeta__TimeSlot=get_timeslot())).distinct()
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

    gt = cache.get("gt"+shortname)
    if gt:
        return gt
    else:
        gt = Group.objects.get(name=fullname)
        cache.set("gt"+shortname, gt, settings.STATIC_OBJECT_CACHE_DURATION)
        return gt


def get_sessions(user):
    sessions = []
    for session in Session.objects.filter(expire_date__gte=timezone.now()):
        data = session.get_decoded()
        if data.get('_auth_user_id', None) == str(user.id):
            sessions.append(session)

    return sessions

