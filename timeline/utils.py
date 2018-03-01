from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Q

from timeline.models import TimeSlot, TimePhase


def get_timeslot():
    """
    Return the current timeslot object. Cached for 15 minutes. If there is not timeslot, it is not cached.
    A timeslot is a half year in which the projects run. It consists of multiple timephases

    :return: object of the first timeslot at this time.
    """
    ts = cache.get('timeslot')
    if ts:
        return ts
    else:
        ts = TimeSlot.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))
        if not ts:
            return None
        cache.set('timeslot', ts[0], settings.STATIC_OBJECT_CACHE_DURATION)
        return ts[0]


def get_timephase():
    """
    Return the current timephase. Cached for 15 minutes. If there is no timephase, it is not cached
    A timephase is a part of a timeslot.

    :return:
    """
    # this also gives false if the timephase is none, so if there is no timephase, it isn't cached
    tp = cache.get('timephase')
    if tp:
        return tp
    else:
        tp = TimePhase.objects.filter(Q(Begin__lte=datetime.now()) & Q(End__gte=datetime.now()))
        if not tp:
            return None
        cache.set('timephase', tp[0], settings.STATIC_OBJECT_CACHE_DURATION)
        return tp[0]


def get_timephase_number():
    """
    return the number of the current timephase, used in a lot of checks. Return -1 if no timephase.

    :return:
    """
    tp = get_timephase()
    if not tp:
        return -1
    return tp.Description


def get_timeslot_id():
    """
    default timeslot for any model connected to timeslot.
    """
    ts = get_timeslot()
    if ts:
        return ts.id
    else:
        raise PermissionDenied("This is not possible, as there is no timeslot.")
