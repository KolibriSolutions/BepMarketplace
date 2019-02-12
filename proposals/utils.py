from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.urls import reverse

from general_view import get_grouptype
from timeline.utils import get_timephase_number, get_timeslot
from .models import Proposal
# from support.utils import group_administrator_status
from support.models import GroupAdministratorThrough


def can_downgrade_project_fn(user, prop):
    if prop.prevyear():
        return False, "This is an old proposal. Changing history is not allowed."

    if prop.Status == 1:
        return False, "Already at first stage."

    # support staf, superusers are always allowed to downgrade
    if get_grouptype("3") in user.groups.all() \
            or user.is_superuser:
        return True, ""

    # proposals of this year, check timephases
    if prop.TimeSlot == get_timeslot():
        # if no timephase is enabled than forbid editing
        if get_timephase_number() < 0:
            return False, "No editing allowed, system is closed"

        # if timephase is after checking phase no editing is allowed, except for support staff
        if get_timephase_number() > 2 and not get_grouptype("3") in user.groups.all():
            return False, "Proposal is frozen in this timeslot"

        # if status is 3 or 4 Responsible can downgrade 3-2 in timephase 1 only
        if prop.Status >= 3 and prop.ResponsibleStaff == user and get_timephase_number() == 1:
            return True, ""

        # Track head can downgrade in phase 1 and 2
        if get_timephase_number() <= 2 and (prop.Track.Head == user or group_administrator_status(prop, user) > 1):
            return True, ""
    else:
        # if status is 3 Responsible can downgrade 3-2 if not in this timeslot
        if prop.Status == 3 and prop.ResponsibleStaff == user:
            return True, ""

        # Track head is allowed all for not this timeslot
        if prop.Track.Head == user or group_administrator_status(prop, user) > 1:
            return True, ""

    # if status is 2 and user is assistant downgrade is allowed
    if prop.Status == 2 \
            and (user in prop.Assistants.all() or prop.ResponsibleStaff == user):
        return True, ""

    return False, ""


def can_edit_project_fn(user, prop, file):
    """
    Check if a user can edit a proposal. Used to show/hide editbuttons on detailproposal and
    for the can_edit_proposal decorator.

    :param user: user
    :param prop: proposal
    :param file: whether editing a file. This is not allowed in limited edit mode (status=4)
    :return: tuple with Boolean and String.
    """
    if prop.prevyear():
        return False, 'This is an old proposal. Changing history is not allowed.'

    # support staf or superusers are always allowed to edit
    if get_grouptype('3') in user.groups.all() or user.is_superuser:
        return True, ''

    # published proposals can only ever be edited limited. choice of form is done in view function
    if prop.Status == 4:
        if (prop.ResponsibleStaff == user or user == prop.Track.Head or group_administrator_status(prop, user) == 2) and not file:
            # file cannot be edited in limited edit.
            return True, ''  # it is the responsibility of the view that the right form is choosen

        if prop.nextyear() or (prop.curyear() and get_timephase_number() < 3):
            if user == prop.Track.Head:
                return False, 'No editing possible. Please downgrade the proposal first.'
            else:
                return False, 'To edit, ask your track head (%s) to downgrade the status of this proposal.' \
                       % prop.Track.Head.usermeta.get_nice_name()
        else:  # later timephases for the current year
            return False, 'No editing possible, the project is already active.'

    # proposals of this year, status 1, 2 and 3.
    if prop.curyear():
        # if no timephase is enabled than forbid editing
        if get_timephase_number() < 0:
            return False, 'No editing allowed, system is closed'

        # if timephase is after checking phase no editing is allowed, except for support staff
        # these unpublished proposals in this timeslot are 'forgotten'. Might be useful for copy but not more.
        if get_timephase_number() > 2:
            return False, 'No editing allowed anymore, not right time phase'

    # track heads are allowed to edit in the create and check phase
    if prop.Track.Head == user or group_administrator_status(prop, user) == 2:
        return True, ''

    # if status is either 1 or 2 and user is assistant edit is allowed in create+check timephase
    if prop.Status < 3 and (user in prop.Assistants.all() or prop.ResponsibleStaff == user):
        return True, ''

    if prop.Status == 3:
        if get_timephase_number() == 2:
            return False, 'To edit, first downgrade the proposal or ask your track head (%s) to do so.' \
                   % prop.Track.Head.usermeta.get_nice_name()
        else:  # timephase 1
            return False, 'To edit, first downgrade the proposal or ask the responsible staff (%s) or track head (%s) to do so.' \
                   % (prop.ResponsibleStaff.usermeta.get_nice_name(), prop.Track.Head.usermeta.get_nice_name())

    # if status is either 1, 2 or 3 and user is track head
    if prop.Status < 4 and prop.Track.Head == user:
        return True, ''

    return False, 'You are not allowed to edit this proposal.'


def get_all_projects(old=False):
    """
    Link to get_all_proposals for consistency with mastermarketplace

    :param old:
    :return:
    """
    return get_all_proposals(old)


def get_all_proposals(old=False):
    """
    All proposals in this timeslot. Cached after timephase 5.

    :return:
    """
    if old:
        return Proposal.objects.all()

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


def get_share_link(pk):
    """
    Create a share link for a proposal detail page.
    Used to let unauthenticated users view a proposal, possibly before the proposal is public.

    :param request:
    :param pk: pk of the proposal to get a link for.
    :return:
    """
    return settings.DOMAIN + reverse('proposals:viewsharelink', args=[signing.dumps(pk)])


def get_cached_project(pk):
    """
    Get a proposal from cache or from database. Put it in cache if it is not yet in cache.

    :param pk: pk of proposal
    :return:
    """
    cprop = cache.get('proposal_{}'.format(pk))
    if cprop is None:
        prop = get_object_or_404(Proposal, pk=pk)
        if prop.Status == 4:
            cache.set('proposal_{}'.format(pk), prop, None)
        return prop
    else:
        return cprop


def updatePropCache(prop):
    """
    Update a cached proposal

    :param prop: proposal object
    :return:
    """
    if prop.Status == 4:
        cache.set('proposal_{}'.format(prop.id), prop, None)


def updatePropCache_pk(pk):
    """
    Update a cached proposal

    :param pk: pk of proposal
    :return:
    """
    prop = get_object_or_404(Proposal, pk=pk)
    if prop.Status == 4:
        cache.set('proposal_{}'.format(pk), prop, None)


def group_administrator_status(project, user):
    """
    Returns the administrator status of user for the group belonging to the project
    status 0: no admin
    status 1: read only admin
    status 2: read/write admin

    :param project:
    :param user:
    :return:
    """
    try:
        g = GroupAdministratorThrough.objects.get(Group=project.Group, User=user)
    except GroupAdministratorThrough.DoesNotExist:
        # for psg in project.SecondaryGroup.all():
        #     try:
        #         gs = GroupAdministratorThrough.objects.get(Group=psg, User=user)
        #     except GroupAdministratorThrough.DoesNotExist:
        #         continue
        #     return 1  # groupadmin of secondary group can only view, not edit.
        return 0  # no primary and no secondary group admin

    # groupadmin of primary group, check super value.
    if g.Super:
        return 2  # rw
    else:
        return 1  # readonly


def get_writable_admingroups(user):
    """
    returns group objects for which this user is writable group admin

    :param user:
    :return:
    """
    return [g.Group for g in GroupAdministratorThrough.objects.filter(User=user, Super=True)]

