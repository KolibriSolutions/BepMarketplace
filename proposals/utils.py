from general_view import get_timephase_number, get_grouptype, get_timeslot


def can_edit_proposal_fn(user, prop):
    """
    Check if a user can edit a proposal. Used to show/hide editbuttons on detailproposal and
    for the can_edit_proposal decorator.

    :param user: user
    :param prop: proposal
    :return: tuple with Boolean and String.
    """
    if prop.prevyear():
        return False, 'This is an old proposal. Changing history is not allowed.'

    # support staf or superusers are always allowed to edit
    if get_grouptype('3') in user.groups.all() or user.is_superuser:
        return True, ''

    # published proposals can never be edited.
    if prop.Status == 4:
        if prop.nextyear() or (prop.curyear() and get_timephase_number() < 3):
            if user == prop.Track.Head:
                return False, 'No editing possible. Please downgrade the proposal first.'
            else:
                return False, 'To edit, ask your track head (%s) to downgrade the status of this proposal.'\
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
            return False, 'To edit, first downgrade the proposal or ask your track head (%s) to do so.'\
                   % prop.Track.Head.usermeta.get_nice_name()
        else:  # timephase 1
            return False, 'To edit, first downgrade the proposal or ask the responsible staff (%s) or track head (%s) to do so.'\
                   % (prop.ResponsibleStaff.usermeta.get_nice_name(), prop.Track.Head.usermeta.get_nice_name())

    # if status is either 1, 2 or 3 and user is track head
    if prop.Status < 4 and prop.Track.Head == user:
        return True, ''

    return False, 'You are not allowed to edit this proposal.'
