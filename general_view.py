from datetime import datetime

from django.contrib.auth.models import Group, User
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing
from django.core.cache import cache
from django.db.models import Q
from django.urls import reverse

from django.conf import settings
from index.models import Track
from proposals.models import Proposal
from students.models import Distribution
from timeline.models import TimeSlot, TimePhase


def createShareLink(request, pk):
    """
    Create a share link for a proposal detail page.
    Used to let unauthenticated users view a proposal, possibly before the proposal is public.
    
    :param request: 
    :param pk: pk of the proposal to get a link for.
    :return: 
    """
    current_site = get_current_site(request)
    domain = current_site.domain
    return "https://" + domain + reverse('api:viewsharelink', args=[signing.dumps(pk)])


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


def get_all_students():
    """
    Return all active students in marketplace, used for instance for mailing.

    :return: user objects
    """

    users = User.objects.filter(Q(usermeta__EnrolledBEP=True)&Q(groups=None) & Q(usermeta__TimeSlot=get_timeslot())).distinct()
    if get_timephase_number() < 6:
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


def get_all_proposals():
    """
    All proposals in this timeslot. Cached after timephase 5.

    :return:
    """
    if get_timephase_number() > 5:
        p = cache.get('all_proposals_objects')
        if p:
            return p
        else:
            p = Proposal.objects.filter(TimeSlot=get_timeslot()).distinct()
            cache.set('all_proposals_objects', p, settings.STATIC_OBJECT_CACHE_DURATION)
            return p
    else:
        return Proposal.objects.filter(TimeSlot=get_timeslot()).distinct()


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