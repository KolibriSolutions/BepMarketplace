#  Bep Marketplace ELE
#  Copyright (c) 2016-2021 Kolibri Solutions
#  License: See LICENSE file or https://github.com/KolibriSolutions/BepMarketplace/blob/master/LICENSE
#
from django.db.models import Q

from general_view import get_grouptype
from index.models import Track
from students.models import Distribution
from timeline.utils import get_timeslot
from presentations.utils import planning_public


def get_distributions(user, timeslot=None):
    """
    Function to return the distributions that a given staff user is allowed to see
    Type3 and 6 should see all distributions, to be able to mail them.

    :param user: The user to test
    :param timeslot: TimeSlot to get distributions from
    :return empty queryset on fail
    """
    if get_grouptype('2u') in user.groups.all():
        return Distribution.objects.none()
    if timeslot is None:
        timeslot = get_timeslot()
        if timeslot is None:
            return Distribution.objects.none()  # similar to None, but can be used in chained filter.
    des_all = Distribution.objects.filter(TimeSlot=timeslot)
    if get_grouptype("3") in user.groups.all() or user.is_superuser or get_grouptype("6") in user.groups.all():
        return des_all
    else:
        tracks = Track.objects.filter(Head=user)
        if planning_public() and timeslot == get_timeslot():
            return des_all.filter(Q(Proposal__Track__in=tracks) |
                                  Q(Proposal__ResponsibleStaff=user) |
                                  Q(Proposal__Assistants__id=user.id) |
                                  Q(presentationtimeslot__Presentations__Assessors__id=user.id)).distinct()
        else:
            return des_all.filter(Q(Proposal__Track__in=tracks) |
                                  Q(Proposal__ResponsibleStaff=user) |
                                  Q(Proposal__Assistants__id=user.id)).distinct()
