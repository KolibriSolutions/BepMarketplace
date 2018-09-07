from django.conf import settings
from django.core import signing
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from django.urls import reverse

from general_view import get_grouptype
from timeline.utils import get_timephase_number, get_timeslot
from .models import Proposal


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
        if (prop.ResponsibleStaff == user or user == prop.Track.Head) and not file:
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
    if prop.Track.Head == user:
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
