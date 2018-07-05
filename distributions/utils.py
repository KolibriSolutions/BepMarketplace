from django.db.models import Q

from general_view import get_grouptype
from index.models import Track
from students.models import Distribution
from timeline.utils import get_timeslot


def get_distributions(user):
    """
    Function to return the distributions that a given staff user is allowed to see
    Type3 and 6 should see all distributions, to be able to mail them.

    :param user: The user to test
    """
    des_all = Distribution.objects.filter(Timeslot=get_timeslot())
    if get_grouptype("3") in user.groups.all() or user.is_superuser or get_grouptype("6") in user.groups.all():
        return des_all
    else:
        tracks = Track.objects.filter(Head=user)
        # TODO only show assessors distributions after presentationsplanning is public
        return des_all.filter(Q(Proposal__Track__in=tracks) |
                              Q(Proposal__ResponsibleStaff=user) |
                              Q(Proposal__Assistants__id= user.id) |
                              Q(presentationtimeslot__Presentations__Assessors__id=user.id)).distinct()
